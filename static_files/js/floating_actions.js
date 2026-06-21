/* دکمه‌های شناور: تماس (FAB) + بازگشت به بالا */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        /* ===== FAB toggle ===== */
        const fabMain      = document.getElementById('fabMain');
        const fabContainer = document.getElementById('fabContainer');
        const fabIcon      = document.getElementById('fabMainIcon');

        if (fabMain && fabContainer) {
            fabMain.addEventListener('click', function (e) {
                e.stopPropagation();
                const isOpen = fabContainer.classList.toggle('open');
                fabMain.classList.toggle('open', isOpen);
                fabMain.setAttribute('aria-expanded', String(isOpen));
                if (fabIcon) {
                    fabIcon.className = isOpen ? 'fa fa-times' : 'fa fa-comment';
                }
            });

            /* بستن با کلیک در هر جای صفحه */
            document.addEventListener('click', function (e) {
                if (fabContainer.classList.contains('open') && !fabContainer.contains(e.target)) {
                    fabContainer.classList.remove('open');
                    fabMain.classList.remove('open');
                    fabMain.setAttribute('aria-expanded', 'false');
                    if (fabIcon) fabIcon.className = 'fa fa-comment';
                }
            });

            /* بستن با Escape */
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && fabContainer.classList.contains('open')) {
                    fabContainer.classList.remove('open');
                    fabMain.classList.remove('open');
                    fabMain.setAttribute('aria-expanded', 'false');
                    if (fabIcon) fabIcon.className = 'fa fa-comment';
                    fabMain.focus();
                }
            });
        }

        /* ===== Back to top ===== */
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            var scrollTimer;
            window.addEventListener('scroll', function () {
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(function () {
                    backToTop.classList.toggle('visible', window.scrollY > 320);
                }, 60);
            }, { passive: true });

            backToTop.addEventListener('click', function () {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

    });
})();
