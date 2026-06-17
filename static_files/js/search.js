/* ============================================================
   سیستم جستجو — باز و بسته کردن پنل اسلاید
   ============================================================ */

(function () {
    'use strict';

    var panel = document.getElementById('searchSlidePanel');
    var input = document.getElementById('searchSlideInput');
    var openBtn = document.getElementById('searchOpenBtn');
    var closeBtn = document.getElementById('searchCloseBtn');

    if (!panel || !openBtn) return;

    function openPanel() {
        panel.classList.add('active');
        if (input) {
            setTimeout(function () { input.focus(); }, 80);
        }
        openBtn.setAttribute('aria-expanded', 'true');
    }

    function closePanel() {
        panel.classList.remove('active');
        openBtn.setAttribute('aria-expanded', 'false');
    }

    openBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (panel.classList.contains('active')) {
            closePanel();
        } else {
            openPanel();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            closePanel();
        });
    }

    /* بستن پنل با کلیک خارج از آن */
    document.addEventListener('click', function (e) {
        if (panel.classList.contains('active') && !panel.contains(e.target) && e.target !== openBtn) {
            closePanel();
        }
    });

    /* بستن پنل با Escape */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && panel.classList.contains('active')) {
            closePanel();
        }
    });
})();
