import logging
import re

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
        kind = str(value.get('type') or '')
        if kind in ('reasoning', 'thinking', 'reasoning_content'):
            return ''
        for key in ('text', 'content', 'value', 'output_text'):
            if key in value and value[key] not in (None, ''):
                found = _plain_text(value[key])
                if found.strip():
                    return found
        return ''
    return ''


def strip_thinking(text):
    """بلوک فکر مدل را از متن قابل‌نمایش جدا می‌کند."""
    cleaned = text or ''
    cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.I | re.S)
    cleaned = re.sub(r'<thinking>.*?</thinking>', '', cleaned, flags=re.I | re.S)
    return cleaned.strip()


def looks_like_reasoning_trace(text):
    """متن برنامه‌ریزی انگلیسی مدل است، نه جواب بیمار."""
    raw = (text or '').strip()
    if not raw:
        return False
    arabic = len(re.findall(r'[\u0600-\u06FF]', raw))
    latin = len(re.findall(r'[A-Za-z]', raw))
    if arabic >= 40:
        return False
    lowered = raw.lower()
    cues = (
        'i think', 'i need', "i'm ", 'i am considering', 'we can discuss',
        'the user', 'i should', 'i want to', 'exploring ', 'evaluating ',
        'proposing ', 'identifying ',
    )
    cue_hit = any(cue in lowered for cue in cues)
    bold_heads = len(re.findall(r'\*\*[A-Za-z][^*]{2,80}\*\*', raw))
    return latin > 80 and (cue_hit or bold_heads >= 1)


def _visible_piece(value):
    text = strip_thinking(_plain_text(value))
    if not text or looks_like_reasoning_trace(text):
        return ''
    return text


def _text_from_chat_json(body):
    """فقط جواب نهایی. فکر درونی مدل، حتی اگر در فیلد reasoning باشد، برنمی‌گردد."""
    if not isinstance(body, dict):
        return ''
    choices = body.get('choices') or []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get('message') or {}
        if not isinstance(message, dict):
            message = {}
        delta = choices[0].get('delta') if isinstance(choices[0].get('delta'), dict) else {}
        for candidate in (
            message.get('content'),
            delta.get('content') if isinstance(delta, dict) else None,
            message.get('reasoning_content'),
            message.get('reasoning'),
        ):
            text = _visible_piece(candidate)
            if text:
                return text
    for key in ('output_text', 'output', 'content'):
        text = _visible_piece(body.get(key))
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


def _openai_client(connection):
    from openai import OpenAI

    if not connection or not connection.base_url or not connection.model_name:
        raise RuntimeError('مدل فعال تنظیم نشده است.')
    api_key = decrypt_secret(connection.api_key_encrypted).strip()
    if not api_key:
        raise RuntimeError('کلید مدل خالی است.')
    return OpenAI(
        api_key=api_key,
        base_url=connection.base_url.strip().rstrip('/'),
        timeout=connection.timeout_seconds or 45,
        max_retries=0,
    )


def _delta_text(chunk):
    choices = getattr(chunk, 'choices', None) or []
    if not choices:
        return ''
    delta = getattr(choices[0], 'delta', None)
    if delta is None:
        return ''
    return _plain_text(getattr(delta, 'content', None))


def iter_completion_text(connection, messages):
    """تکه‌های متن را همان لحظه که مدل می‌نویسد برمی‌گرداند."""
    client = _openai_client(connection)
    prepared = _to_openai_messages(messages)
    max_tokens = connection.max_tokens or 800
    temperature = connection.temperature if connection.temperature is not None else 0.3
    variants = [
        {'temperature': temperature, 'max_tokens': max_tokens, 'stream': True},
        {'stream': True},
    ]
    last_error = 'پاسخ مدل خالی بود.'
    for extra in variants:
        started = False
        try:
            stream = client.chat.completions.create(
                model=connection.model_name.strip(),
                messages=prepared,
                **extra,
            )
            for chunk in stream:
                text = _delta_text(chunk)
                if not text:
                    continue
                started = True
                yield text
            return
        except Exception as exc:
            last_error = str(exc)
            logger.exception('استریم مدل ناموفق')
            if started:
                raise
    raise RuntimeError(last_error)


def complete_text(connection, messages):
    """جواب مدل از بدنهٔ خام. اگر کتابخانه متن را خالی ببیند، باز هم همان جواب لیارا خوانده می‌شود."""
    client = _openai_client(connection)
    prepared = _to_openai_messages(messages)
    max_tokens = connection.max_tokens or 800
    temperature = connection.temperature if connection.temperature is not None else 0.3
    # فکر کردن مدل را خاموش می‌کنیم تا به‌جای جواب، متن انگلیسی برنامه‌ریزی نیاید
    thinking_off = {
        'extra_body': {
            'enable_thinking': False,
            'chat_template_kwargs': {'enable_thinking': False},
        },
    }
    attempts = [
        {'messages': prepared, 'temperature': temperature, 'max_tokens': max_tokens, **thinking_off},
        {
            'messages': prepared,
            'temperature': temperature,
            'max_completion_tokens': max(max_tokens, 2000),
            **thinking_off,
        },
        {'messages': prepared, 'temperature': temperature, 'max_tokens': max_tokens},
        {
            'messages': prepared + [{
                'role': 'user',
                'content': (
                    'فقط پاسخ نهایی را به زبان بیمار بنویس. '
                    'فکر درونی، عنوان انگلیسی و برنامه‌ریزی ننویس. تشخیص قطعی و دارو نده.'
                ),
            }],
            'temperature': temperature,
            'max_completion_tokens': max(max_tokens, 2000),
            **thinking_off,
        },
    ]
    def read_attempt(extra):
        kwargs = {
            'model': connection.model_name.strip(),
            'messages': extra['messages'],
        }
        for key, value in extra.items():
            if key != 'messages':
                kwargs[key] = value
        raw = client.chat.completions.with_raw_response.create(**kwargs)
        response = raw.http_response
        try:
            body = response.json()
        except Exception:
            body = {}
        if response.status_code >= 400:
            err = body.get('error') if isinstance(body, dict) else None
            message = _plain_text((err or {}).get('message') if isinstance(err, dict) else err) or str(response.status_code)
            return 'error', message
        text = _text_from_chat_json(body)
        if text:
            return 'ok', text
        return 'empty', 'پاسخ مدل متن قابل نمایش نداشت.'

    last_error = 'پاسخ مدل خالی بود.'
    saw_empty_answer = False
    for extra in attempts[:-1]:
        try:
            kind, payload = read_attempt(extra)
        except Exception as exc:
            last_error = str(exc)
            logger.exception('خواندن پاسخ مدل ناموفق')
            continue
        if kind == 'ok':
            return payload
        last_error = payload
        if kind == 'empty':
            saw_empty_answer = True
            break
    if saw_empty_answer or last_error:
        try:
            kind, payload = read_attempt(attempts[-1])
            if kind == 'ok':
                return payload
            last_error = payload
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
