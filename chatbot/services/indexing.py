import logging
from pathlib import Path

from django.utils import timezone

from chatbot.engine.rag import get_vectorstore
from chatbot.models import KnowledgeFile

logger = logging.getLogger('chatbot')


def _splitter():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)


def _read_file_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {'.txt', '.md'}:
        return path.read_text(encoding='utf-8', errors='ignore')
    if ext == '.pdf':
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or '')
        return '\n'.join(pages)
    raise ValueError(f'فرمت پشتیبانی نمی‌شود: {ext}')


def add_file_to_rag(knowledge_file: KnowledgeFile) -> str:
    knowledge_file.status = 'indexing'
    knowledge_file.save(update_fields=['status'])
    store = get_vectorstore(knowledge_file.profile)
    if store is None:
        knowledge_file.status = 'error'
        knowledge_file.last_error = 'اتصال embedding فعال نیست یا Chroma در دسترس نیست.'
        knowledge_file.in_rag = False
        knowledge_file.save(update_fields=['status', 'last_error', 'in_rag'])
        return knowledge_file.last_error

    path = Path(knowledge_file.file.path)
    try:
        text = _read_file_text(path).strip()
        if not text:
            raise ValueError('متن قابل استخراج از فایل نبود (شاید PDF اسکن‌شده باشد).')
        chunks = _splitter().split_text(text)
        ids = [f'file-{knowledge_file.pk}-{i}' for i in range(len(chunks))]
        metadatas = [
            {'source': knowledge_file.original_name, 'file_id': str(knowledge_file.pk)}
            for _ in chunks
        ]
        # اول قطعات قبلی همین فایل را بردار، بعد از نو بنویس
        _delete_file_vectors(store, knowledge_file.pk)
        store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
        knowledge_file.in_rag = True
        knowledge_file.status = 'ready'
        knowledge_file.chunk_count = len(chunks)
        knowledge_file.last_error = ''
        knowledge_file.indexed_at = timezone.now()
        knowledge_file.save()
        return ''
    except Exception as exc:
        logger.exception('ایندکس فایل RAG ناموفق')
        knowledge_file.status = 'error'
        knowledge_file.in_rag = False
        knowledge_file.last_error = str(exc)
        knowledge_file.save(update_fields=['status', 'in_rag', 'last_error'])
        return str(exc)


def remove_file_from_rag(knowledge_file: KnowledgeFile, delete_file=False):
    store = get_vectorstore(knowledge_file.profile)
    if store is not None:
        _delete_file_vectors(store, knowledge_file.pk)
    knowledge_file.in_rag = False
    knowledge_file.status = 'idle'
    knowledge_file.chunk_count = 0
    knowledge_file.save(update_fields=['in_rag', 'status', 'chunk_count'])
    if delete_file:
        knowledge_file.file.delete(save=False)
        knowledge_file.delete()


def _delete_file_vectors(store, file_id):
    try:
        store._collection.delete(where={'file_id': str(file_id)})
    except Exception:
        # برخی نسخه‌های Chroma where را متفاوت می‌خواهند
        try:
            store.delete(ids=[f'file-{file_id}-{i}' for i in range(5000)])
        except Exception:
            logger.exception('حذف بردارهای فایل از Chroma ناموفق')


def rebuild_profile_rag(profile):
    """بعد از عوض شدن مدل embedding فایل‌ها و محتوای انتخاب‌شدهٔ سایت از نو ایندکس می‌شوند."""
    from chatbot.services.site_index import sync_profile_sources
    errors = []
    for item in profile.knowledge_files.filter(in_rag=True):
        err = add_file_to_rag(item)
        if err:
            errors.append(f'{item.original_name}: {err}')
    errors.extend(sync_profile_sources(profile))
    return errors
