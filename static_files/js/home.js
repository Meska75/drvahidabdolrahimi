/* ==============================================
   صفحه اصلی — home.js
   دکتر وحید عبدالرحیمی
============================================== */

(function ($) {
    "use strict";

    $(function () {

        /* ===== slider crossfade بنر هیرو ===== */
        var slides = document.querySelectorAll('#heroBgSlider .hero-slide');
        var current = 0;
        slides.forEach(function (s) {
            var bg = s.getAttribute('data-bg');
            if (bg) s.style.backgroundImage = 'url(' + bg + ')';
        });
        if (slides.length > 0) {
            slides[0].classList.add('active');
            setInterval(function () {
                slides[current].classList.remove('active');
                current = (current + 1) % slides.length;
                slides[current].classList.add('active');
            }, 5000);
        }

        /* ===== کاروسل خدمات — فعال فقط اگر تعداد آیتم > 4 ===== */
        function initSrvCarousel(el) {
            var $el = $(el);
            if (!$el.length) return;
            if ($el.children('.srv-carousel-item').length > 4) {
                $el.owlCarousel({
                    loop: true, margin: 20, autoplay: true,
                    autoplayTimeout: 3500, autoplayHoverPause: true,
                    nav: true, dots: true,
                    navText: ['<i class="fa fa-chevron-right"></i>', '<i class="fa fa-chevron-left"></i>'],
                    smartSpeed: 700,
                    responsive: { 0: { items: 1 }, 576: { items: 2 }, 992: { items: 3 }, 1200: { items: 4 } }
                });
            }
        }
        initSrvCarousel($('#officeSrvCarousel'));
        initSrvCarousel($('#surgerySrvCarousel'));

        /* ===== تصویر fade پس‌زمینه بخش تیم ===== */
        var $bgImg = $('#teamBgImg');
        var $bgOvl = $('.team-bg-overlay');
        var bgTimer = null;

        $('.team-card').on('mouseenter', function () {
            var url = $(this).attr('data-bg');
            if (!url) return;
            clearTimeout(bgTimer);
            $bgImg[0].style.backgroundImage = 'url("' + url + '")';
            $bgImg.addClass('active');
            $bgOvl.addClass('active');
        }).on('mouseleave', function () {
            bgTimer = setTimeout(function () {
                $bgImg.removeClass('active');
                $bgOvl.removeClass('active');
            }, 250);
        });

        /* ===== lightbox گالری ===== */
        var $lb = $('#galleryLightbox');
        var $lbImg = $('#lbImg');

        $(document).on('click', '.gallery-item', function () {
            var full = $(this).attr('data-full') || $(this).find('img').attr('src');
            $lbImg.attr('src', full);
            $lb.addClass('open');
            $('body').css('overflow', 'hidden');
        });

        $('#lbClose').on('click', closeLb);

        $lb.on('click', function (e) {
            if (e.target === this) closeLb();
        });

        $(document).on('keydown', function (e) {
            if (e.key === 'Escape') closeLb();
        });

        function closeLb() {
            $lb.removeClass('open');
            $('body').css('overflow', '');
        }

    });

})(jQuery);


/* ===== نقشه نشان (Leaflet + tile API نشان) =====
   window.load: بعد از defer scripts اجرا می‌شود */
window.addEventListener('load', function () {
    var mapEl = document.getElementById('neshanMap');
    if (!mapEl || typeof L === 'undefined') return;

    var lat    = 35.75431655694686;
    var lng    = 51.41248217613625;
    var apiKey = 'service.4b130a29422349a7a3210bf2972459f5';

    var map = L.map('neshanMap', {
        center: [lat, lng],
        zoom: 16,
        zoomControl: true,
        attributionControl: true
    });

    /* tile نشان با fallback به OpenStreetMap */
    var neshanFailed = false;
    var neshanLayer  = L.tileLayer(
        'https://map.neshan.org/sdk/v1/map/xyz/dreamy/{z}/{x}/{y}.png?x-api-key=' + apiKey,
        { attribution: '© <a href="https://neshan.org" target="_blank">نشان</a>', maxZoom: 18 }
    );

    neshanLayer.on('tileerror', function () {
        if (!neshanFailed) {
            neshanFailed = true;
            map.removeLayer(neshanLayer);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://openstreetmap.org" target="_blank">OpenStreetMap</a>'
            }).addTo(map);
        }
    });

    neshanLayer.addTo(map);

    L.marker([lat, lng])
        .addTo(map)
        .bindPopup(
            '<div dir="rtl" style="font-family:Vazirmatn,sans-serif;font-size:13px;padding:4px 8px;">' +
            '<strong>مطب دکتر وحید عبدالرحیمی</strong></div>'
        )
        .openPopup();

    /* رفع اندازه container در flex layout */
    setTimeout(function () { map.invalidateSize(); }, 300);
});
