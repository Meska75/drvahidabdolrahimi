/* ===================================================
   home_ar.js — صفحة الرئيسية العربية
   مشابه لـ home.js (RTL) مع محتوى عربي
=================================================== */

$(function () {

    /* ===== Crossfade Hero Slider ===== */
    var slides  = $('.hero-slide');
    var total   = slides.length;
    var current = 0;

    function loadBg(el) {
        var src = el.data('bg');
        if (src && !el.data('loaded')) {
            el.css('background-image', 'url(' + src + ')');
            el.data('loaded', true);
        }
    }

    if (total > 0) {
        loadBg(slides.eq(0));
        slides.eq(0).addClass('active');

        if (total > 1) {
            setInterval(function () {
                var next = (current + 1) % total;
                loadBg(slides.eq(next));
                slides.eq(current).removeClass('active');
                slides.eq(next).addClass('active');
                current = next;
            }, 5000);
        }
    }

    /* ===== Team Background ===== */
    var teamBg = document.getElementById('teamBgImg');
    if (teamBg) {
        var src = $(teamBg).data('bg');
        if (src) teamBg.style.backgroundImage = 'url(' + src + ')';
    }

    /* ===== Office Services Carousel (RTL) ===== */
    var $offCar = $('#officeSrvCarousel');
    if ($offCar.length) {
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

    /* ===== Surgery Services Carousel (RTL) ===== */
    var $surCar = $('#surgerySrvCarousel');
    if ($surCar.length) {
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


/* ===== Swiper آراء المرضى ===== */
if (typeof Swiper !== 'undefined' && document.querySelector('.tst-swiper')) {
    /* تكرار الشرائح حتى 8 لضمان حلقة لا نهائية سلسة */
    (function () {
        var wrapper = document.querySelector('.tst-swiper .swiper-wrapper');
        if (!wrapper) return;
        var orig = Array.from(wrapper.querySelectorAll('.swiper-slide'));
        if (!orig.length) return;
        var i = 0;
        while (wrapper.querySelectorAll('.swiper-slide').length < 8) {
            wrapper.appendChild(orig[i % orig.length].cloneNode(true));
            i++;
        }
    })();

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
}


/* ===== خريطة نشان (Leaflet) ===== */
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
            '<div dir="rtl" style="font-family:Cairo,sans-serif;font-size:13px;padding:4px 8px;">' +
            '<strong>عيادة د. وحيد عبد الرحيمي</strong></div>'
        )
        .openPopup();

    setTimeout(function () { map.invalidateSize(); }, 300);
});
