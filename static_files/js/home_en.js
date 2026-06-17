(function ($) {
    "use strict";

    $(function () {

        /* ===== Hero banner crossfade slider ===== */
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

        /* ===== Services carousel — active only when items > 4 ===== */
        function initSrvCarousel(el) {
            var $el = $(el);
            if (!$el.length) return;
            if ($el.children('.srv-carousel-item').length > 4) {
                $el.owlCarousel({
                    loop: true, margin: 20, autoplay: true,
                    autoplayTimeout: 3500, autoplayHoverPause: true,
                    nav: true, dots: true,
                    navText: ['<i class="fa fa-chevron-left"></i>', '<i class="fa fa-chevron-right"></i>'],
                    smartSpeed: 700,
                    responsive: { 0: { items: 1 }, 576: { items: 2 }, 992: { items: 3 }, 1200: { items: 4 } }
                });
            }
        }
        initSrvCarousel($('#officeSrvCarousel'));
        initSrvCarousel($('#surgerySrvCarousel'));

        /* ===== Team section — background fade on hover ===== */
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

        /* ===== Gallery lightbox ===== */
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


/* ===== Swiper Patient Testimonials ===== */
if (typeof Swiper !== 'undefined' && document.querySelector('.tst-swiper')) {
    /* duplicate slides to at least 8 so loop: true is always seamless */
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


/* ===== Map (Leaflet + Neshan tile) ===== */
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
        { attribution: '© <a href="https://neshan.org" target="_blank">Neshan</a>', maxZoom: 18 }
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
            '<div style="font-family:Inter,sans-serif;font-size:13px;padding:4px 8px;">' +
            '<strong>Dr. Vahid Abdolrahimi\'s Clinic</strong></div>'
        )
        .openPopup();

    setTimeout(function () { map.invalidateSize(); }, 300);
});
