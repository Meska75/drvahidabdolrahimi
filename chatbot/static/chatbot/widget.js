(function () {
    var root = document.getElementById('dr-chatbot-root');
    if (!root) return;

    var COPY = {
        fa: {
            launcher: 'پرسش از دستیار',
            title: 'دستیار مطب',
            sub: 'پاسخ‌ها جنبه آموزشی دارند و جایگزین معاینه نیستند.',
            placeholder: 'پیام خود را بنویسید…',
            statusSearch: 'در حال بررسی اطلاعات مطب…',
            statusWrite: 'در حال نوشتن پاسخ…',
            failed: 'پاسخ آماده نشد. لطفاً یک‌بار دیگر بفرستید.',
            close: 'بستن',
            clear: 'پاک کردن گفتگو',
            clearConfirm: 'گفتگوی فعلی پاک شود؟'
        },
        en: {
            launcher: 'Ask the assistant',
            title: 'Clinic assistant',
            sub: 'Answers are educational and not a medical exam.',
            placeholder: 'Type your message…',
            statusSearch: 'Checking clinic information…',
            statusWrite: 'Writing the answer…',
            failed: 'The reply was not ready. Please send it once more.',
            close: 'Close',
            clear: 'Clear chat',
            clearConfirm: 'Clear this conversation?'
        },
        ar: {
            launcher: 'اسأل المساعد',
            title: 'مساعد العيادة',
            sub: 'الإجابات للمعرفة العامة وليست بديلاً عن الفحص.',
            placeholder: 'اكتب رسالتك…',
            statusSearch: 'جارٍ مراجعة معلومات العيادة…',
            statusWrite: 'جارٍ كتابة الإجابة…',
            failed: 'لم يجهز الرد. أعد الإرسال مرة أخرى.',
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

    var sending = false;

    function thinkingBubble() {
        var el = document.createElement('div');
        el.className = 'dr-chat-bubble assistant dr-chat-pending';
        el.innerHTML = '<div class="dr-chat-status"></div><div class="dr-chat-dots" aria-hidden="true"><i></i><i></i><i></i></div>';
        el.querySelector('.dr-chat-status').textContent = copy.statusSearch;
        messages.appendChild(el);
        messages.scrollTop = messages.scrollHeight;
        return el;
    }

    function setStatus(el, text) {
        if (!el.classList.contains('dr-chat-pending')) return;
        var node = el.querySelector('.dr-chat-status');
        if (node) node.textContent = text;
    }

    function parseSseBlock(block) {
        var data = [];
        block.split('\n').forEach(function (line) {
            line = line.replace(/\r$/, '');
            if (line.indexOf('data:') === 0) data.push(line.slice(5).replace(/^\s/, ''));
        });
        if (!data.length) return null;
        try {
            return JSON.parse(data.join('\n'));
        } catch (e) {
            return null;
        }
    }

    function sendMessage(text) {
        if (sending) return;
        sending = true;
        input.disabled = true;
        bubble('user', text);
        input.value = '';
        var live = thinkingBubble();
        var queue = '';
        var shown = '';
        var pumping = false;
        var finished = false;

        function paint() {
            if (!shown) return;
            live.classList.remove('dr-chat-pending');
            live.classList.add('dr-chat-live');
            live.textContent = shown;
            messages.scrollTop = messages.scrollHeight;
        }

        function endLive() {
            live.classList.remove('dr-chat-pending');
            live.classList.remove('dr-chat-live');
            if (!shown) live.textContent = copy.failed;
        }

        function pump() {
            if (pumping) return;
            pumping = true;
            function step() {
                if (!queue) {
                    pumping = false;
                    if (finished) endLive();
                    return;
                }
                var n = queue.length;
                if (n > 120) n = 8;
                else if (n > 40) n = 4;
                else if (n > 8) n = 2;
                shown += queue.slice(0, n);
                queue = queue.slice(n);
                paint();
                requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        }

        function fail() {
            finished = true;
            queue = '';
            if (!shown) {
                live.classList.remove('dr-chat-pending');
                live.textContent = copy.failed;
            }
        }

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
            if (!response.ok || !response.body) {
                fail();
                return;
            }
            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var buffer = '';
            function read() {
                return reader.read().then(function (result) {
                    buffer += decoder.decode(result.value || new Uint8Array(), { stream: !result.done });
                    var parts = buffer.split('\n\n');
                    buffer = parts.pop();
                    parts.forEach(function (block) {
                        var payload = parseSseBlock(block);
                        if (!payload) return;
                        if (payload.status === 'search') setStatus(live, copy.statusSearch);
                        if (payload.status === 'write') setStatus(live, copy.statusWrite);
                        if (payload.reset) {
                            shown = '';
                            queue = '';
                        }
                        if (payload.token && !payload.done) queue += payload.token;
                        if (payload.done && payload.session) token = payload.session;
                        if (payload.done) finished = true;
                        if (payload.token && !payload.done) pump();
                    });
                    if (!result.done) return read();
                    if (buffer.trim()) {
                        var tail = parseSseBlock(buffer);
                        if (tail) {
                            if (tail.reset) {
                                shown = '';
                                queue = '';
                            }
                            if (tail.token && !tail.done) queue += tail.token;
                            if (tail.done && tail.session) token = tail.session;
                        }
                    }
                    finished = true;
                    if (queue && !pumping) pump();
                    else if (!queue) endLive();
                });
            }
            return read();
        }).catch(fail).then(function () {
            sending = false;
            input.disabled = false;
            input.focus();
        });
    }

    input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            if (form.requestSubmit) form.requestSubmit();
            else form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        var text = (input.value || '').trim();
        if (!text || sending) return;
        sendMessage(text);
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
