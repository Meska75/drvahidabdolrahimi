"""حافظه گفتگو به سبک LangChain فعلی: BaseChatMessageHistory + trim_messages.

جدول همان Conversation/ChatMessage جنگو است تا در پنل ادمین دیده شود.
"""

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, trim_messages

from chatbot.models import ChatMessage


def _approx_tokens(messages):
    """شمارش تقریبی توکن بدون فراخوانی مدل — حدود ۴ کاراکتر = ۱ توکن."""
    if isinstance(messages, list):
        return sum(_approx_tokens(m) for m in messages)
    content = getattr(messages, 'content', '') or ''
    if isinstance(content, list):
        content = ' '.join(str(part) for part in content)
    return max(1, len(str(content)) // 4)


class DjangoConversationHistory(BaseChatMessageHistory):
    """تاریخچه یک گفتگو — معادل SQLChatMessageHistory روی مدل‌های خودمان."""

    def __init__(self, conversation):
        self.conversation = conversation

    @property
    def messages(self):
        rows = []
        for item in self.conversation.messages.order_by('created_at'):
            if item.role == 'user':
                rows.append(HumanMessage(content=item.content))
            else:
                rows.append(AIMessage(content=item.content))
        return rows

    def add_message(self, message: BaseMessage):
        role = 'user' if message.type in ('human', 'user') else 'assistant'
        ChatMessage.objects.create(
            conversation=self.conversation,
            role=role,
            content=message.content if isinstance(message.content, str) else str(message.content),
        )

    def clear(self):
        self.conversation.messages.all().delete()


def _clip(text, limit):
    raw = text or ''
    if len(raw) <= limit:
        return raw
    return raw[:limit].rstrip() + '…'


def messages_for_model(system_text, rag_context, history_messages, question, max_tokens=800):
    """پرامپت سیستم + تاریخچهٔ کوتاه + سؤال فعلی. سقف تاریخچه حدود ۸۰۰ توکن است."""
    system_parts = [system_text]
    context = _clip((rag_context or '').strip(), 2600)
    if context:
        system_parts.append('دانش مطب:\n' + context)

    past = []
    for message in history_messages or []:
        content = _clip(getattr(message, 'content', '') or '', 400)
        if isinstance(message, HumanMessage):
            past.append(HumanMessage(content=content))
        else:
            past.append(AIMessage(content=content))
    if past and isinstance(past[-1], HumanMessage) and past[-1].content == question:
        past = past[:-1]

    trimmed = trim_messages(
        past,
        max_tokens=max_tokens,
        strategy='last',
        token_counter=_approx_tokens,
        start_on='human',
        include_system=False,
        allow_partial=False,
    )
    return (
        [SystemMessage(content='\n\n'.join(system_parts))]
        + list(trimmed)
        + [HumanMessage(content=question)]
    )
