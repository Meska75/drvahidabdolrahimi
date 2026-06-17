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
