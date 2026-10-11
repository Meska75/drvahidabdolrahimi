/* ===================================================
   home_ar.js — صفحة الرئيسية العربية
   مشابه لـ home.js (RTL) مع محتوى عربي
=================================================== */

$(function () {

    /* ===== Crossfade Hero Slider — الصورة الأولى في HTML لاكتشاف LCP ===== */
    var slides = document.querySelectorAll('#heroBgSlider .hero-slide');
    if (slides.length > 1) {
        var current = 0;
        if (!slides[0].classList.contains('active')) {
            slides[0].classList.add('active');
        }
        setInterval(function () {
            slides[current].classList.remove('active');
            current = (current + 1) % slides.length;
            slides[current].classList.add('active');
        }, 5000);
    }

    /* ===== Team Background ===== */
    var teamBg = document.getElementById('teamBgImg');
    if (teamBg) {
        var src = $(teamBg).data('bg');
        if (src) teamBg.style.backgroundImage = 'url(' + src + ')';
    }

    /* ===== Office / Surgery carousels — after lazy Owl ===== */
    if (window.whenVendor) {
        whenVendor('owl', function () {
            var $offCar = $('#officeSrvCarousel');
            if ($offCar.length && $.fn.owlCarousel && !$offCar.hasClass('owl-loaded')) {
                $offCar.owlCarousel({
                    rtl: true,
                    loop: true,
                    margin: 24,
                    nav: true,
                    dots: false,
                    navText: ['<i class="fa fa-chevron-right"></i>', '<i class="fa fa-chevron-left"></i>'],
                    responsive: { 0: { items: 1 }, 576: { items: 2 }, 992: { items: 3 } }
                });
            }
            var $surCar = $('#surgerySrvCarousel');
            if ($surCar.length && $.fn.owlCarousel && !$surCar.hasClass('owl-loaded')) {
                $surCar.owlCarousel({
                    rtl: true,
                    loop: true,
                    margin: 24,
                    nav: true,
                    dots: false,
                    navText: ['<i class="fa fa-chevron-right"></i>', '<i class="fa fa-chevron-left"></i>'],
                    responsive: { 0: { items: 1 }, 576: { items: 2 }, 992: { items: 3 } }
                });
            }
        });
    }

    /* ===== Gallery Lightbox ===== */
    var $lb    = $('#galleryLightbox');
    var $lbImg = $('#lbImg');
    var $lbClose = $('#lbClose');

    $('.gallery-item').on('click', function () {
        var full = $(this).data('full');
        if (full) {
            $lbImg.attr('src', full).attr('alt', $(this).find('img').attr('alt') || '');
            $lb.addClass('active');
            $('body').css('overflow', 'hidden');
        }
    });

    function closeLb() {
        $lb.removeClass('active');
        $('body').css('overflow', '');
        setTimeout(function () { $lbImg.attr('src', ''); }, 300);
    }

    $lbClose.on('click', closeLb);
    $lb.on('click', function (e) { if ($(e.target).is($lb)) closeLb(); });
    $(document).on('keydown', function (e) { if (e.key === 'Escape') closeLb(); });

    /* ===== Team Card Hover ===== */
    $('.team-card').each(function () {
        var bg = $(this).data('bg');
        if (bg) {
            $(this).on('mouseenter', function () {
                $('#teamBgImg').css('background-image', 'url(' + bg + ')');
            });
        }
    });

});


/* ===== Swiper آراء المرضى — بعد التحميل الكسول ===== */
if (window.whenVendor) {
    whenVendor('swiper', function () {
        if (typeof Swiper === 'undefined' || !document.querySelector('.tst-swiper')) return;
        var wrapper = document.querySelector('.tst-swiper .swiper-wrapper');
        if (wrapper) {
            var orig = Array.from(wrapper.querySelectorAll('.swiper-slide'));
            var i = 0;
            while (orig.length && wrapper.querySelectorAll('.swiper-slide').length < 8) {
                wrapper.appendChild(orig[i % orig.length].cloneNode(true));
                i++;
            }
        }
        new Swiper('.tst-swiper', {
            loop: true,
            speed: 600,
            autoplay: { delay: 5000, disableOnInteraction: false },
            centeredSlides: true,
            grabCursor: true,
            spaceBetween: 30,
            navigation: {
                nextEl: '.tst-swiper .swiper-button-next',
                prevEl: '.tst-swiper .swiper-button-prev',
            },
            breakpoints: {
                0:    { slidesPerView: 1,   spaceBetween: 16 },
                768:  { slidesPerView: 1.5, spaceBetween: 24 },
                1100: { slidesPerView: 3,   spaceBetween: 30 },
            }
        });
    });
}


/* ===== خريطة — بعد لود تنبل Leaflet ===== */
if (window.whenVendor) {
    whenVendor('leaflet', function () {
        var mapEl = document.getElementById('neshanMap');
        if (!mapEl || typeof L === 'undefined' || mapEl._leaflet_id) return;

        var lat = 35.75431655694686;
        var lng = 51.41248217613625;

        var map = L.map('neshanMap', {
            center: [lat, lng],
            zoom: 16,
            zoomControl: true,
            attributionControl: true
        });

        // آدرس قدیمی کاشی نشان ۴۰۴ است و tile.openstreetmap.org هم به‌خاطر
        // Referrer-Policy: same-origin تصویر «Access blocked» برمی‌گرداند.
        L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
            maxZoom: 19,
            referrerPolicy: 'strict-origin-when-cross-origin'
        }).addTo(map);

        L.marker([lat, lng])
            .addTo(map)
            .bindPopup(
                '<div dir="rtl" style="font-family:Cairo,sans-serif;font-size:13px;padding:4px 8px;">' +
                '<strong>عيادة د. وحيد عبد الرحيمي</strong></div>'
            )
            .openPopup();

        setTimeout(function () { map.invalidateSize(); }, 300);
    });
}
