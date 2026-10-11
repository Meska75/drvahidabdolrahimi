from django.test import TestCase

from langchain_core.messages import AIMessage, HumanMessage

from chatbot.engine.fallback import fallback_text
from chatbot.engine.greetings import greeting_text
from chatbot.engine.memory import messages_for_model
from chatbot.engine.safety import SAFETY_POLICY, looks_like_prescription_request
from chatbot.protect.bot_detect import honeypot_filled, issue_token, token_is_valid


class GreetingTests(TestCase):
    def test_greeting_uses_page_language(self):
        fa = greeting_text('fa', 'دستیار تست')
        en = greeting_text('en', 'Test assistant')
        ar = greeting_text('ar', 'مساعد')
        self.assertIn('سلام', fa)
        self.assertIn('Hello', en)
        self.assertIn('مرحبا', ar)

    def test_fallback_does_not_mention_outage(self):
        for lang in ('fa', 'en', 'ar'):
            text = fallback_text(lang).lower()
            self.assertNotIn('api', text)
            self.assertNotIn('لیارا', text)
            self.assertNotIn('model', text)
            self.assertNotIn('قطع', text)


class SafetyTests(TestCase):
    def test_policy_forbids_prescription(self):
        self.assertIn('تجویز', SAFETY_POLICY)

    def test_detects_drug_request(self):
        self.assertTrue(looks_like_prescription_request('چه قطره‌ای بخرم؟'))


class BotDetectTests(TestCase):
    def test_honeypot(self):
        self.assertTrue(honeypot_filled({'website': 'http://spam'}))
        self.assertTrue(honeypot_filled({'dr_hp': 'http://spam'}))
        self.assertFalse(honeypot_filled({'website': ''}))
        self.assertFalse(honeypot_filled({'dr_hp': ''}))

    def test_token_roundtrip(self):
        token = issue_token()
        self.assertTrue(token_is_valid(token))


class ReasoningTraceTests(TestCase):
    def test_english_planning_is_not_an_answer(self):
        from chatbot.engine.llm import _text_from_chat_json, looks_like_reasoning_trace

        trace = (
            '**Exploring vision phenomena**\n\n'
            'We can discuss possible causes of vision changes. '
            'I think it is important to recommend an in-person exam. '
            'I need to avoid giving a diagnosis.'
        )
        self.assertTrue(looks_like_reasoning_trace(trace))
        body = {'choices': [{'message': {
            'content': trace,
            'reasoning_content': trace,
        }}]}
        self.assertEqual(_text_from_chat_json(body), '')

    def test_persian_answer_is_kept_when_reasoning_is_separate(self):
        from chatbot.engine.llm import _text_from_chat_json

        answer = (
            'هاله خاکستری وسط دید علت‌های مختلفی دارد و از اینجا تشخیص قطعی ممکن نیست. '
            'برای بررسی شبکیه باید معاینه حضوری انجام شود.'
        )
        body = {'choices': [{'message': {
            'content': answer,
            'reasoning_content': '**Evaluating causes of halos** I think about cataracts.',
        }}]}
        self.assertEqual(_text_from_chat_json(body), answer)

    def test_think_tags_are_removed(self):
        from chatbot.engine.llm import _text_from_chat_json

        body = {'choices': [{'message': {
            'content': '<think>plan the answer in English</think>معاینه حضوری لازم است و تشخیص قطعی داده نمی‌شود.',
        }}]}
        text = _text_from_chat_json(body)
        self.assertNotIn('think', text.lower())
        self.assertIn('معاینه حضوری', text)


class ReplyShapeTests(TestCase):
    def test_repeated_intro_is_removed(self):
        from chatbot.engine.chat import iter_visible, visible_reply

        raw = (
            'سلام. من دستیار هوش مصنوعی مطب دکتر عبدالرحیمی هستم.\n\n'
            'لیزیک در این مطب انجام می‌شود.'
        )
        text = visible_reply(raw, 'fa', 'لیزیک دارید؟')
        self.assertNotIn('دستیار هوش مصنوعی', text)
        self.assertIn('لیزیک', text)

        pieces = list(iter_visible([raw], 'fa', 'خدمات مطب چیست'))
        self.assertEqual(len(pieces), 1)
        self.assertIn('لیزیک', pieces[0])
        self.assertNotIn('من دستیار', pieces[0])

    def test_identity_question_keeps_intro(self):
        from chatbot.engine.chat import visible_reply

        raw = 'سلام. من دستیار هوش مصنوعی مطب هستم.'
        self.assertIn('دستیار', visible_reply(raw, 'fa', 'تو کی هستی؟'))

    def test_prompt_forbids_repeating_intro(self):
        from chatbot.engine.prompts import build_system_prompt

        class Profile:
            assistant_name_fa = 'دستیار تست'
            assistant_name_en = 'Test'
            assistant_name_ar = 'مساعد'
            prompt_fa = ''
            prompt_en = ''
            prompt_ar = ''
            knowledge_mode = 'hybrid'

        text = build_system_prompt(Profile(), 'fa')
        self.assertIn('خودت را معرفی نکن', text)
        self.assertNotIn('قطعه‌ای بازیابی نشد', text)


class SiteContextTests(TestCase):
    def test_answer_uses_site_services_without_embeddings(self):
        from chatbot.engine.rag import retrieve_context
        from chatbot.models import ChatbotProfile
        from services.models import ServiceItem

        profile = ChatbotProfile.objects.create(
            slug='test-clinic',
            title='تست',
            is_default=True,
            knowledge_mode='hybrid',
        )
        ServiceItem.objects.create(
            type='surgery',
            title_fa='لیزیک اختصاصی این مطب',
            description_fa='اصلاح عیب انکساری با لیزر در همین مرکز',
        )
        text = retrieve_context(profile, 'خدمات جراحی لیزیک چیست', language='fa')
        self.assertIn('لیزیک اختصاصی این مطب', text)

    def test_about_page_biography_is_included(self):
        from chatbot.services.site_index import _about_page_text

        text = _about_page_text('fa')
        self.assertIn('شبکیه', text)
        self.assertIn('عبدالرحیمی', text)


class MemoryTrimTests(TestCase):
    def test_trim_keeps_recent_human_question(self):
        past = []
        for i in range(20):
            past.append(HumanMessage(content='سؤال قدیمی ' * 40 + str(i)))
            past.append(AIMessage(content='پاسخ قدیمی ' * 40 + str(i)))
        packed = messages_for_model('سیستم', '', past, 'سؤال جدید', max_tokens=200)
        self.assertEqual(packed[-1].content, 'سؤال جدید')
        self.assertTrue(len(packed) < len(past) + 2)
