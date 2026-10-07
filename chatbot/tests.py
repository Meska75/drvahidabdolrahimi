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
        self.assertFalse(honeypot_filled({'website': ''}))

    def test_token_roundtrip(self):
        token = issue_token()
        self.assertTrue(token_is_valid(token))


class MemoryTrimTests(TestCase):
    def test_trim_keeps_recent_human_question(self):
        past = []
        for i in range(20):
            past.append(HumanMessage(content='سؤال قدیمی ' * 40 + str(i)))
            past.append(AIMessage(content='پاسخ قدیمی ' * 40 + str(i)))
        packed = messages_for_model('سیستم', '', past, 'سؤال جدید', max_tokens=200)
        self.assertEqual(packed[-1].content, 'سؤال جدید')
        self.assertTrue(len(packed) < len(past) + 2)
