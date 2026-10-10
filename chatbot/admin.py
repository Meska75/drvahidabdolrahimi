from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from chatbot.engine.llm import ping_chat_model, ping_embedding_model
from chatbot.models import (
    ChatbotProfile, LlmConnection, EmbeddingConnection,
    KnowledgeFile, Conversation, ChatMessage,
)
from chatbot.services.indexing import add_file_to_rag, remove_file_from_rag, rebuild_profile_rag
from chatbot.services.site_index import SITE_SOURCES, remove_source, sync_profile_sources
from chatbot.services.secrets import decrypt_secret, encrypt_secret, mask_secret


class SecretInputMixin:
    """کلید را در فرم خالی نشان می‌دهد؛ اگر پر شود رمز می‌شود. خالی = بدون تغییر."""

    secret_field = 'api_key_encrypted'
    secret_form_field = 'api_key_plain'

    def save_model(self, request, obj, form, change):
        incoming = (form.cleaned_data.get(self.secret_form_field) or '').strip()
        if incoming:
            setattr(obj, self.secret_field, encrypt_secret(incoming))
        super().save_model(request, obj, form, change)


class ChatbotProfileForm(forms.ModelForm):
    link_api_key_plain = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password'}),
        label='کلید نسخه لینک (اگر خالی بماند عوض نمی‌شود)',
        help_text='سایت دیگر این کلید را در هدر X-Chatbot-Key می‌فرستد.',
    )

    class Meta:
        model = ChatbotProfile
        fields = '__all__'
        exclude = ('link_api_key_encrypted',)


class LlmConnectionForm(forms.ModelForm):
    api_key_plain = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password'}),
        label='کلید دسترسی مدل چت',
        help_text='اگر خالی بماند کلید قبلی می‌ماند.',
    )

    class Meta:
        model = LlmConnection
        fields = '__all__'
        exclude = ('api_key_encrypted', 'is_ready', 'last_error')


class EmbeddingConnectionForm(forms.ModelForm):
    api_key_plain = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password'}),
        label='کلید دسترسی مدل RAG',
        help_text='معمولاً همان کلید مدل چت.',
    )

    class Meta:
        model = EmbeddingConnection
        fields = '__all__'
        exclude = ('api_key_encrypted', 'is_ready', 'last_error', 'fingerprint')


class LlmInline(admin.TabularInline):
    model = LlmConnection
    extra = 1
    fields = ('name', 'model_name', 'provider', 'is_ready')
    readonly_fields = ('is_ready',)
    show_change_link = True


class EmbeddingInline(admin.TabularInline):
    model = EmbeddingConnection
    extra = 1
    fields = ('name', 'model_name', 'provider', 'is_ready')
    readonly_fields = ('is_ready',)
    show_change_link = True


@admin.register(ChatbotProfile)
class ChatbotProfileAdmin(SecretInputMixin, admin.ModelAdmin):
    form = ChatbotProfileForm
    secret_field = 'link_api_key_encrypted'
    secret_form_field = 'link_api_key_plain'
    list_display = (
        'title', 'slug', 'widget_enabled', 'link_enabled',
        'knowledge_mode', 'active_llm', 'active_embedding',
    )
    list_editable = ('widget_enabled', 'link_enabled')
    inlines = [LlmInline, EmbeddingInline]
    fieldsets = (
        ('شناسه', {
            'fields': ('title', 'slug', 'is_default'),
        }),
        ('روشن / خاموش', {
            'description': 'با خاموش کردن «نمایش آیکون»، ویجت از سایت این پروفایل حذف می‌شود.',
            'fields': ('widget_enabled', 'link_enabled'),
        }),
        ('منبع پاسخ', {
            'fields': ('knowledge_mode', 'active_llm', 'active_embedding'),
        }),
        ('محتوای خود سایت در RAG', {
            'description': (
                'بخش‌های تیک‌خورده در جستجوی ویجت و نسخه لینک همین پروفایل می‌آیند. '
                'فایل‌های آپلودی جدا هستند و پاک نمی‌شوند. '
                'بعد از انتخاب، دکمهٔ «ایندکس محتوای فعلی سایت» را بزنید. '
                'با تیک خودکار، ذخیره یا حذف بعدی همان بخش‌ها خودش RAG را عوض می‌کند. '
                'پیام تماس و نظر بیماران وارد RAG نمی‌شوند.'
            ),
            'fields': (
                'sync_site_faq', 'sync_site_services', 'sync_site_doctor',
                'sync_site_clinic', 'sync_site_team', 'sync_site_blog',
                'sync_site_auto', 'index_site_button',
            ),
        }),
        ('نام دستیار و پرامپت', {
            'fields': (
                'assistant_name_fa', 'prompt_fa',
                'assistant_name_en', 'prompt_en',
                'assistant_name_ar', 'prompt_ar',
            ),
        }),
        ('نسخه لینک (سایت دیگر)', {
            'fields': ('link_api_key_plain', 'current_link_key', 'allowed_origins'),
        }),
        ('محدودیت ضد اسپم', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_hour'),
        }),
    )
    readonly_fields = ('current_link_key', 'index_site_button')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['active_llm'].queryset = obj.llm_connections.all()
            form.base_fields['active_embedding'].queryset = obj.embedding_connections.all()
        return form

    @admin.display(description='کلید لینک فعلی (ماسک)')
    def current_link_key(self, obj):
        return mask_secret(decrypt_secret(obj.link_api_key_encrypted)) or '—'

    @admin.display(description='ایندکس سایت')
    def index_site_button(self, obj):
        if not obj.pk:
            return 'ابتدا ذخیره کنید'
        url = reverse('admin:chatbot_index_site', args=[obj.pk])
        return format_html('<a class="button" href="{}">ایندکس محتوای فعلی سایت</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                '<int:pk>/index-site/',
                self.admin_site.admin_view(self.index_site_view),
                name='chatbot_index_site',
            ),
        ]
        return extra + urls

    def index_site_view(self, request, pk):
        obj = get_object_or_404(ChatbotProfile, pk=pk)
        errors = sync_profile_sources(obj)
        if errors:
            messages.error(request, 'ایندکس سایت ناقص ماند: ' + ' | '.join(errors[:4]))
        else:
            messages.success(request, 'محتوای انتخاب‌شدهٔ سایت در RAG این پروفایل قرار گرفت.')
        return redirect('admin:chatbot_chatbotprofile_change', obj.pk)

    def save_model(self, request, obj, form, change):
        previous = ChatbotProfile.objects.filter(pk=obj.pk).first() if obj.pk else None
        super().save_model(request, obj, form, change)
        if obj.is_default:
            ChatbotProfile.objects.exclude(pk=obj.pk).update(is_default=False)
        if previous:
            for name in SITE_SOURCES:
                was_on = getattr(previous, f'sync_site_{name}')
                is_on = getattr(obj, f'sync_site_{name}')
                if was_on and not is_on:
                    err = remove_source(obj, name)
                    if err:
                        messages.warning(request, f'حذف {name} از RAG: {err}')


@admin.register(LlmConnection)
class LlmConnectionAdmin(SecretInputMixin, admin.ModelAdmin):
    form = LlmConnectionForm
    list_display = ('name', 'profile', 'model_name', 'provider', 'is_ready', 'test_button')
    list_filter = ('profile', 'provider', 'is_ready')
    readonly_fields = ('is_ready', 'last_error', 'current_key', 'test_button')
    fieldsets = (
        (None, {'fields': ('profile', 'name')}),
        ('درگاه مدل', {
            'description': 'سه مقدار لازم: Base URL + کلید + نام مدل. روش اتصال معمولاً OpenAI سازگار است.',
            'fields': ('provider', 'base_url', 'api_key_plain', 'current_key', 'model_name', 'azure_api_version'),
        }),
        ('تنظیم پاسخ', {
            'fields': ('temperature', 'max_tokens', 'timeout_seconds'),
        }),
        ('وضعیت', {
            'fields': ('is_ready', 'last_error', 'test_button'),
        }),
    )

    @admin.display(description='کلید (ماسک)')
    def current_key(self, obj):
        return mask_secret(decrypt_secret(obj.api_key_encrypted)) or '—'

    @admin.display(description='تست')
    def test_button(self, obj):
        if not obj.pk:
            return 'ابتدا ذخیره کنید'
        url = reverse('admin:chatbot_test_llm', args=[obj.pk])
        return format_html('<a class="button" href="{}">تست اتصال</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                '<int:pk>/test/',
                self.admin_site.admin_view(self.test_view),
                name='chatbot_test_llm',
            ),
        ]
        return extra + urls

    def test_view(self, request, pk):
        obj = get_object_or_404(LlmConnection, pk=pk)
        ok, detail = ping_chat_model(obj)
        obj.is_ready = ok
        obj.last_error = '' if ok else detail
        obj.save(update_fields=['is_ready', 'last_error'])
        if ok:
            messages.success(request, 'اتصال مدل چت موفق بود.')
        else:
            messages.error(request, f'اتصال ناموفق (فقط ادمین می‌بیند): {detail}')
        return redirect('admin:chatbot_llmconnection_change', obj.pk)


@admin.register(EmbeddingConnection)
class EmbeddingConnectionAdmin(SecretInputMixin, admin.ModelAdmin):
    form = EmbeddingConnectionForm
    list_display = ('name', 'profile', 'model_name', 'provider', 'is_ready', 'test_button')
    list_filter = ('profile', 'provider', 'is_ready')
    readonly_fields = (
        'is_ready', 'last_error', 'current_key', 'test_button',
        'rebuild_button', 'fingerprint',
    )
    fieldsets = (
        (None, {'fields': ('profile', 'name')}),
        ('اتصال embedding', {
            'description': 'اگر مدل embedding عوض شود باید فایل‌های RAG از نو ایندکس شوند.',
            'fields': ('provider', 'base_url', 'api_key_plain', 'current_key', 'model_name', 'azure_api_version'),
        }),
        ('وضعیت', {
            'fields': (
                'timeout_seconds', 'is_ready', 'last_error', 'fingerprint',
                'test_button', 'rebuild_button',
            ),
        }),
    )

    @admin.display(description='کلید (ماسک)')
    def current_key(self, obj):
        return mask_secret(decrypt_secret(obj.api_key_encrypted)) or '—'

    @admin.display(description='تست')
    def test_button(self, obj):
        if not obj.pk:
            return 'ابتدا ذخیره کنید'
        url = reverse('admin:chatbot_test_embedding', args=[obj.pk])
        return format_html('<a class="button" href="{}">تست اتصال</a>', url)

    @admin.display(description='بازسازی RAG')
    def rebuild_button(self, obj):
        if not obj.pk:
            return 'ابتدا ذخیره کنید'
        url = reverse('admin:chatbot_rebuild_rag', args=[obj.pk])
        return format_html('<a class="button" href="{}">بازسازی ایندکس همه فایل‌ها</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                '<int:pk>/test/',
                self.admin_site.admin_view(self.test_view),
                name='chatbot_test_embedding',
            ),
            path(
                '<int:pk>/rebuild/',
                self.admin_site.admin_view(self.rebuild_view),
                name='chatbot_rebuild_rag',
            ),
        ]
        return extra + urls

    def test_view(self, request, pk):
        obj = get_object_or_404(EmbeddingConnection, pk=pk)
        ok, detail = ping_embedding_model(obj)
        obj.is_ready = ok
        obj.last_error = '' if ok else detail
        obj.fingerprint = obj.compute_fingerprint()
        obj.save(update_fields=['is_ready', 'last_error', 'fingerprint'])
        if ok:
            messages.success(request, 'اتصال embedding موفق بود.')
        else:
            messages.error(request, f'اتصال ناموفق: {detail}')
        return redirect('admin:chatbot_embeddingconnection_change', obj.pk)

    def rebuild_view(self, request, pk):
        obj = get_object_or_404(EmbeddingConnection, pk=pk)
        errors = rebuild_profile_rag(obj.profile)
        if errors:
            messages.error(request, 'بازسازی ناقص: ' + ' | '.join(errors[:5]))
        else:
            messages.success(request, 'ایندکس RAG از نو ساخته شد.')
        return redirect('admin:chatbot_embeddingconnection_change', obj.pk)

    def save_model(self, request, obj, form, change):
        old = None
        if obj.pk:
            old = EmbeddingConnection.objects.filter(pk=obj.pk).first()
        super().save_model(request, obj, form, change)
        new_fp = obj.compute_fingerprint()
        if old and old.fingerprint and old.fingerprint != new_fp:
            messages.warning(
                request,
                'مدل RAG عوض شد. از دکمه «بازسازی ایندکس» استفاده کنید وگرنه جستجو نادرست می‌شود.',
            )
        obj.fingerprint = new_fp
        obj.save(update_fields=['fingerprint'])


@admin.register(KnowledgeFile)
class KnowledgeFileAdmin(admin.ModelAdmin):
    list_display = (
        'original_name', 'profile', 'in_rag', 'status',
        'chunk_count', 'uploaded_at',
    )
    list_filter = ('profile', 'in_rag', 'status')
    search_fields = ('original_name',)
    readonly_fields = (
        'original_name', 'status', 'chunk_count', 'last_error',
        'indexed_at', 'uploaded_at',
    )
    actions = ['action_add_to_rag', 'action_remove_from_rag']
    fields = (
        'profile', 'file', 'original_name', 'in_rag',
        'status', 'chunk_count', 'indexed_at', 'last_error',
    )

    @admin.action(description='افزودن به RAG (از کتابخانه یا فایل جدید)')
    def action_add_to_rag(self, request, queryset):
        for item in queryset:
            err = add_file_to_rag(item)
            if err:
                messages.error(request, f'{item.original_name}: {err}')
            else:
                messages.success(request, f'{item.original_name} به RAG اضافه شد.')

    @admin.action(description='خارج کردن از RAG (فایل در کتابخانه می‌ماند)')
    def action_remove_from_rag(self, request, queryset):
        for item in queryset:
            remove_file_from_rag(item, delete_file=False)
        messages.success(request, 'فایل‌ها از ایندکس RAG برداشته شدند و در کتابخانه ماندند.')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.in_rag:
            err = add_file_to_rag(obj)
            if err:
                messages.error(request, f'ایندکس نشد: {err}')
            else:
                messages.success(request, 'فایل ایندکس شد و در RAG قرار گرفت.')


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'used_fallback', 'internal_error', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'language', 'source', 'ip_address', 'created_at')
    list_filter = ('profile', 'language', 'source')
    inlines = [ChatMessageInline]
    readonly_fields = (
        'profile', 'session_key', 'language', 'source',
        'ip_address', 'created_at', 'updated_at',
    )

    def has_add_permission(self, request):
        return False
