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
        # استریم بعضی درگاه‌ها مثل لیارا قطع نمی‌شود و چت روی سه‌نقطه می‌ماند
        'disable_streaming': True,
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


def _plain_text(value):
    """متن قابل نمایش از رشته، لیست یا شیء. لیارا گاهی content را لیست برمی‌گرداند."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return ''.join(_plain_text(item) for item in value)
    if isinstance(value, dict):
        for key in ('text', 'content', 'value', 'output_text', 'reasoning_content'):
            if key in value and value[key] not in (None, ''):
                found = _plain_text(value[key])
                if found.strip():
                    return found
        return ''
    return ''


def _text_from_chat_json(body):
    if not isinstance(body, dict):
        return ''
    choices = body.get('choices') or []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get('message') or {}
        if not isinstance(message, dict):
            message = {}
        for candidate in (
            message.get('content'),
            (choices[0].get('delta') or {}).get('content') if isinstance(choices[0].get('delta'), dict) else None,
            message.get('reasoning_content'),
            message.get('reasoning'),
        ):
            text = _plain_text(candidate).strip()
            if text:
                return text
    for key in ('output_text', 'output', 'content'):
        text = _plain_text(body.get(key)).strip()
        if text:
            return text
    return ''


def _to_openai_messages(messages):
    role_of = {
        'system': 'system',
        'human': 'user',
        'ai': 'assistant',
        'user': 'user',
        'assistant': 'assistant',
    }
    prepared = []
    for message in messages:
        if isinstance(message, dict):
            role = message.get('role') or 'user'
            content = message.get('content') or ''
        else:
            role = role_of.get(getattr(message, 'type', ''), 'user')
            content = getattr(message, 'content', '') or ''
        prepared.append({'role': role, 'content': _plain_text(content)})
    return prepared


def complete_text(connection, messages):
    """جواب مدل از بدنهٔ خام. اگر کتابخانه متن را خالی ببیند، باز هم همان جواب لیارا خوانده می‌شود."""
    from openai import OpenAI

    if not connection or not connection.base_url or not connection.model_name:
        raise RuntimeError('مدل فعال تنظیم نشده است.')
    api_key = decrypt_secret(connection.api_key_encrypted).strip()
    if not api_key:
        raise RuntimeError('کلید مدل خالی است.')
    client = OpenAI(
        api_key=api_key,
        base_url=connection.base_url.strip().rstrip('/'),
        timeout=connection.timeout_seconds or 45,
        max_retries=0,
    )
    prepared = _to_openai_messages(messages)
    max_tokens = connection.max_tokens or 800
    temperature = connection.temperature if connection.temperature is not None else 0.3
    attempts = [
        {'temperature': temperature, 'max_tokens': max_tokens},
        {'temperature': temperature, 'max_completion_tokens': max(max_tokens, 2000)},
        {},
    ]
    last_error = 'پاسخ مدل خالی بود.'
    for extra in attempts:
        kwargs = {
            'model': connection.model_name.strip(),
            'messages': prepared,
        }
        kwargs.update(extra)
        try:
            raw = client.chat.completions.with_raw_response.create(**kwargs)
            response = raw.http_response
            try:
                body = response.json()
            except Exception:
                body = {}
            if response.status_code >= 400:
                err = body.get('error') if isinstance(body, dict) else None
                last_error = _plain_text((err or {}).get('message') if isinstance(err, dict) else err) or str(response.status_code)
                continue
            text = _text_from_chat_json(body)
            if text:
                return text
            last_error = 'پاسخ مدل متن قابل نمایش نداشت.'
        except Exception as exc:
            last_error = str(exc)
            logger.exception('خواندن پاسخ مدل ناموفق')
    raise RuntimeError(last_error)


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
