(function () {
    var root = document.getElementById('dr-chatbot-root');
    if (!root) return;

    var COPY = {
        fa: {
            launcher: 'پرسش از دستیار',
            title: 'دستیار مطب',
            sub: 'پاسخ‌ها جنبه آموزشی دارند و جایگزین معاینه نیستند.',
            placeholder: 'پیام خود را بنویسید…',
            close: 'بستن',
            clear: 'پاک کردن گفتگو',
            clearConfirm: 'گفتگوی فعلی پاک شود؟'
        },
        en: {
            launcher: 'Ask the assistant',
            title: 'Clinic assistant',
            sub: 'Answers are educational and not a medical exam.',
            placeholder: 'Type your message…',
            close: 'Close',
            clear: 'Clear chat',
            clearConfirm: 'Clear this conversation?'
        },
        ar: {
            launcher: 'اسأل المساعد',
            title: 'مساعد العيادة',
            sub: 'الإجابات للمعرفة العامة وليست بديلاً عن الفحص.',
            placeholder: 'اكتب رسالتك…',
            close: 'إغلاق',
            clear: 'مسح المحادثة',
            clearConfirm: 'هل تريد مسح هذه المحادثة؟'
        }
    };

    var lang = root.getAttribute('data-lang') || 'fa';
    var copy = COPY[lang] || COPY.fa;
    var token = '';
    var greetingText = '';
    var threadReady = false;

    var launcher = document.getElementById('drChatbotLauncher');
    var panel = document.getElementById('drChatbotPanel');
    var closer = document.getElementById('drChatbotClose');
    var clearer = document.getElementById('drChatbotClear');
    var messages = document.getElementById('drChatbotMessages');
    var form = document.getElementById('drChatbotForm');
    var input = document.getElementById('drChatbotInput');

    launcher.querySelector('.dr-chatbot-launcher-label').textContent = copy.launcher;
    root.querySelector('.dr-chatbot-title').textContent = copy.title;
    root.querySelector('.dr-chatbot-sub').textContent = copy.sub;
    closer.setAttribute('aria-label', copy.close);
    if (clearer) clearer.setAttribute('aria-label', copy.clear);
    if (clearer) clearer.setAttribute('title', copy.clear);
    input.setAttribute('placeholder', copy.placeholder);

    function csrf() {
        var input = form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input && input.value) return input.value;
        var match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function honeypotValue() {
        var field = form.querySelector('input[name="dr_hp"]');
        return field ? field.value : '';
    }

    function bubble(role, text) {
        var el = document.createElement('div');
        el.className = 'dr-chat-bubble ' + role;
        el.textContent = text;
        messages.appendChild(el);
        messages.scrollTop = messages.scrollHeight;
        return el;
    }

    function renderMessages(list) {
        messages.innerHTML = '';
        (list || []).forEach(function (item) {
            bubble(item.role === 'user' ? 'user' : 'assistant', item.content || '');
        });
    }

    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf()
            },
            body: JSON.stringify(body)
        }).then(function (r) { return r.json(); });
    }

    function showGreetingIfEmpty() {
        if (messages.childElementCount || !greetingText) return;
        renderMessages([{ role: 'assistant', content: greetingText }]);
    }

    function loadThread() {
        return postJson(root.getAttribute('data-start'), {
            language: lang,
            dr_hp: honeypotValue(),
            token: token
        }).then(function (data) {
            if (!data || data.ok === false) throw new Error('start failed');
            threadReady = true;
            if (data.greeting) greetingText = data.greeting;
            if (data.token) token = data.token;
            if (data.messages && data.messages.length) {
                renderMessages(data.messages);
            } else {
                showGreetingIfEmpty();
            }
        });
    }

    function openPanel() {
        panel.hidden = false;
        launcher.setAttribute('aria-expanded', 'true');
        if (!threadReady) {
            showGreetingIfEmpty();
            loadThread().catch(function () {
                threadReady = false;
                showGreetingIfEmpty();
            });
        }
        input.focus();
    }

    function closePanel() {
        panel.hidden = true;
        launcher.setAttribute('aria-expanded', 'false');
    }

    launcher.addEventListener('click', function () {
        if (panel.hidden) openPanel();
        else closePanel();
    });
    closer.addEventListener('click', closePanel);

    if (clearer) {
        clearer.addEventListener('click', function () {
            if (!window.confirm(copy.clearConfirm)) return;
            postJson(root.getAttribute('data-clear'), {
                language: lang,
                dr_hp: honeypotValue(),
                token: token
            }).then(function (data) {
                if (data.token) token = data.token;
                renderMessages(data.messages || []);
            }).catch(function () {});
        });
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        var text = (input.value || '').trim();
        if (!text) return;
        bubble('user', text);
        input.value = '';
        var live = bubble('assistant', '…');
        fetch(root.getAttribute('data-stream'), {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf()
            },
            body: JSON.stringify({
                language: lang,
                message: text,
                token: token,
                dr_hp: honeypotValue()
            })
        }).then(function (response) {
            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var buffer = '';
            var acc = '';
            function read() {
                return reader.read().then(function (result) {
                    buffer += decoder.decode(result.value || new Uint8Array(), { stream: !result.done });
                    var parts = buffer.split('\n\n');
                    buffer = parts.pop();
                    parts.forEach(function (block) {
                        var line = block.replace(/^data:\s*/, '');
                        if (!line) return;
                        try {
                            var payload = JSON.parse(line);
                            if (payload.done) {
                                if (payload.token) token = payload.token;
                                return;
                            }
                            if (payload.reset) acc = '';
                            if (payload.token) {
                                acc += payload.token;
                                live.textContent = acc;
                                messages.scrollTop = messages.scrollHeight;
                            }
                        } catch (e) {}
                    });
                    if (!result.done) return read();
                });
            }
            return read();
        }).catch(function () {
            live.textContent = copy.sub;
        });
    });

    fetch(root.getAttribute('data-config') + '?lang=' + encodeURIComponent(lang), {
        credentials: 'same-origin'
    }).then(function (r) { return r.json(); }).then(function (data) {
        if (!data.enabled) {
            root.hidden = true;
            return;
        }
        token = data.token || '';
        greetingText = data.greeting || greetingText;
        if (data.name) {
            root.querySelector('.dr-chatbot-title').textContent = data.name;
        }
        if (!panel.hidden) showGreetingIfEmpty();
        root.hidden = false;
    }).catch(function () {});

    window.addEventListener('pageshow', function (event) {
        if (!event.persisted) return;
        if (!messages.childElementCount) threadReady = false;
    });
})();
