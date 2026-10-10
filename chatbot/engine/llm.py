import logging
from chatbot.services.secrets import decrypt_secret

logger = logging.getLogger('chatbot')


def build_chat_model(connection):
    """مدل چت LangChain از روی اتصال پنل (درگاه سازگار با OpenAI)."""
    from langchain_openai import ChatOpenAI

    if not connection or not connection.base_url or not connection.model_name:
        return None
    api_key = decrypt_secret(connection.api_key_encrypted)
    if not api_key:
        return None

    kwargs = {
        'model': connection.model_name,
        'api_key': api_key,
        'base_url': connection.base_url.rstrip('/'),
        'temperature': connection.temperature or 0.3,
        'timeout': connection.timeout_seconds or 45,
        'max_tokens': connection.max_tokens or 800,
    }
    if connection.provider == 'azure' and connection.azure_api_version:
        kwargs['default_query'] = {'api-version': connection.azure_api_version}
    return ChatOpenAI(**kwargs)


def build_embedding_model(connection):
    from langchain_openai import OpenAIEmbeddings

    if not connection or not connection.base_url or not connection.model_name:
        return None
    api_key = decrypt_secret(connection.api_key_encrypted)
    if not api_key:
        return None
    kwargs = {
        'model': connection.model_name.strip(),
        'api_key': api_key.strip(),
        'base_url': connection.base_url.strip().rstrip('/'),
        'timeout': connection.timeout_seconds or 60,
        # LangChain پیش‌فرض متن را به شناسه توکن تبدیل می‌کند؛ لیارا فقط متن خام می‌پذیرد
        'check_embedding_ctx_length': False,
        # SDK اوپن‌ای اگر این مقدار نیاید base64 می‌فرستد و درگاه لیارا همان درخواست را 401 می‌دهد
        'model_kwargs': {'encoding_format': 'float'},
    }
    if connection.provider == 'azure' and connection.azure_api_version:
        kwargs['default_query'] = {'api-version': connection.azure_api_version}
    return OpenAIEmbeddings(**kwargs)


def ping_chat_model(connection):
    """تست اتصال برای پنل ادمین. خطا برای کاربر سایت برنمی‌گردد."""
    try:
        model = build_chat_model(connection)
        if model is None:
            return False, 'لینک، کلید یا نام مدل خالی است.'
        model.invoke('ping')
        return True, 'اتصال موفق بود.'
    except Exception as exc:
        logger.exception('تست مدل چت ناموفق')
        return False, str(exc)


def ping_embedding_model(connection):
    try:
        model = build_embedding_model(connection)
        if model is None:
            return False, 'لینک، کلید یا نام مدل خالی است.'
        model.embed_query('test')
        return True, 'اتصال embedding موفق بود.'
    except Exception as exc:
        logger.exception('تست embedding ناموفق')
        text = str(exc)
        if '401' in text or 'Unauthorized' in text:
            return False, (
                'کلید یا Base URL این اتصال RAG را لیارا نپذیرفت. '
                'همان مقادیر اتصال چت را دوباره بنویسید و ذخیره کنید؛ '
                'اگر فیلد کلید خالی بماند کلید قبلی عوض نمی‌شود. '
                + text
            )
        return False, text
