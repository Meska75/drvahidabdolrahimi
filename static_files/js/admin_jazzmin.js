/* تغییر placeholder فیلد یوزرنیم در صفحه لاگین */
(function () {
    var usernameInput = document.getElementById('id_username');
    if (usernameInput) {
        usernameInput.placeholder = 'یوزرنیم، ایمیل یا شماره موبایل';
        var label = document.querySelector('label[for="id_username"]');
        if (label) label.textContent = 'نام کاربری';
    }
    var passwordInput = document.getElementById('id_password');
    if (passwordInput) {
        passwordInput.placeholder = 'رمز عبور';
    }
})();

/* ============================================================
   مدیریت sidebar — بدون تداخل با localStorage مرورگر
   ریشه کرش: AdminLTE وضعیت sidebar-collapse را در localStorage
   ذخیره می‌کرد و هر بار لود اعمال می‌شد.
   راه‌حل: sidebar-collapse را به admin-sidebar-closed تبدیل کن
   تا localStorage آن را ذخیره نکند.
   ============================================================ */
(function () {

    /* ۱. پاک کردن وضعیت قدیمی sidebar از localStorage */
    try {
        Object.keys(localStorage).forEach(function (k) {
            if (k.indexOf('sidebar') !== -1 || k.indexOf('lte') !== -1) {
                localStorage.removeItem(k);
            }
        });
    } catch (e) {}

    /* ۲. حذف فوری کلاسی که AdminLTE ممکن است بازیابی کرده باشد */
    document.body.classList.remove('sidebar-collapse');

    /* ۳. رهگیری sidebar-collapse و تبدیل به کلاس اختصاصی */
    var intercepting = false;

    var sidebarWatcher = new MutationObserver(function (mutations) {
        if (intercepting) return;
        for (var i = 0; i < mutations.length; i++) {
            if (mutations[i].attributeName === 'class') {
                if (document.body.classList.contains('sidebar-collapse')) {
                    intercepting = true;

                    /* حذف کلاس AdminLTE و toggle کلاس اختصاصی */
                    document.body.classList.remove('sidebar-collapse');
                    document.body.classList.toggle('admin-sidebar-closed');

                    /* پاک کردن مجدد localStorage */
                    try {
                        Object.keys(localStorage).forEach(function (k) {
                            if (k.indexOf('sidebar') !== -1 || k.indexOf('lte') !== -1) {
                                localStorage.removeItem(k);
                            }
                        });
                    } catch (e) {}

                    setTimeout(function () { intercepting = false; }, 150);
                    break;
                }
            }
        }
    });

    sidebarWatcher.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
    });

    /* ۴. overlay تاریک برای بستن sidebar در موبایل */
    var overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    overlay.addEventListener('click', function () {
        document.body.classList.remove('sidebar-open');
    });

})();
