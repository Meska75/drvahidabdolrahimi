"""جستجوی RAG داخل دیتابیس خود سایت. کتابخانهٔ Chroma لازم نیست."""

import logging
import math

from chatbot.models import KnowledgeChunk

logger = logging.getLogger('chatbot')


def _cosine(left, right):
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = norm_left = norm_right = 0.0
    for a, b in zip(left, right):
        dot += a * b
        norm_left += a * a
        norm_right += b * b
    if norm_left == 0 or norm_right == 0:
        return 0.0
    return dot / (math.sqrt(norm_left) * math.sqrt(norm_right))


def embedding_client(profile):
    from chatbot.engine.llm import build_embedding_model
    if profile is None:
        return None
    return build_embedding_model(profile.active_embedding)


def _embed_texts(client, texts):
    vectors = []
    size = 16
    for start in range(0, len(texts), size):
        batch = texts[start:start + size]
        vectors.extend(client.embed_documents(batch))
    return vectors


def replace_chunks(profile, rows):
    """rows: دیکشنری‌های text, source_type, source_key, source_label."""
    if not rows:
        return ''
    client = embedding_client(profile)
    if client is None:
        return 'اتصال embedding فعال نیست.'
    try:
        vectors = _embed_texts(client, [row['text'] for row in rows])
    except Exception as exc:
        logger.exception('ساخت بردار ناموفق')
        return str(exc)
    keys = {row['source_key'] for row in rows}
    KnowledgeChunk.objects.filter(profile=profile, source_key__in=keys).delete()
    KnowledgeChunk.objects.bulk_create([
        KnowledgeChunk(
            profile=profile,
            source_type=row['source_type'],
            source_key=row['source_key'],
            source_label=row.get('source_label') or row['source_key'],
            text=row['text'],
            embedding=vector,
        )
        for row, vector in zip(rows, vectors)
    ])
    return ''


def delete_chunks(profile, *, source_type=None, source_key=None):
    qs = KnowledgeChunk.objects.filter(profile=profile)
    if source_type:
        qs = qs.filter(source_type=source_type)
    if source_key:
        qs = qs.filter(source_key=source_key)
    qs.delete()
    return ''


def retrieve_context(profile, question, k=4):
    if profile.knowledge_mode == 'llm_only':
        return ''
    client = embedding_client(profile)
    if client is None:
        return ''
    try:
        query_vector = client.embed_query(question)
    except Exception:
        logger.exception('بردار سؤال ساخته نشد')
        return ''
    ranked = []
    for chunk in KnowledgeChunk.objects.filter(profile=profile).iterator():
        ranked.append((_cosine(query_vector, chunk.embedding), chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    parts = []
    for index, (_score, chunk) in enumerate(ranked[:k], start=1):
        if _score <= 0:
            continue
        parts.append(f'[{index}] ({chunk.source_label})\n{chunk.text}')
    return '\n\n'.join(parts)
