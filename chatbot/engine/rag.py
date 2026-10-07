import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('chatbot')


def chroma_dir():
    path = Path(getattr(settings, 'CHATBOT_CHROMA_DIR', settings.BASE_DIR / 'chatbot_store' / 'chroma'))
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def collection_name(profile):
    return f'clinic_{profile.slug}'


def get_vectorstore(profile):
    """اگر embedding یا chromadb در دسترس نباشد None برمی‌گردد."""
    from chatbot.engine.llm import build_embedding_model

    connection = profile.active_embedding
    embeddings = build_embedding_model(connection)
    if embeddings is None:
        return None
    try:
        from langchain_chroma import Chroma
        return Chroma(
            collection_name=collection_name(profile),
            embedding_function=embeddings,
            persist_directory=chroma_dir(),
        )
    except Exception:
        logger.exception('باز کردن Chroma ناموفق')
        return None


def retrieve_context(profile, question, k=4):
    if profile.knowledge_mode == 'llm_only':
        return ''
    store = get_vectorstore(profile)
    if store is None:
        return ''
    try:
        docs = store.similarity_search(question, k=k)
    except Exception:
        logger.exception('جستجوی RAG ناموفق')
        return ''
    parts = []
    for i, doc in enumerate(docs, start=1):
        source = (doc.metadata or {}).get('source', '')
        parts.append(f'[{i}] ({source})\n{doc.page_content}')
    return '\n\n'.join(parts)
