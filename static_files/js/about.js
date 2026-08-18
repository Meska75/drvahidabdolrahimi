(function ($) {
    "use strict";

    function initClinicsSlider() {
        if (!$.fn.owlCarousel || !$('.clinics-slider').length) return;
        if ($('.clinics-slider').hasClass('owl-loaded')) return;
        $('.clinics-slider').owlCarousel({
            rtl: true,
            loop: true,
            margin: 20,
            dots: true,
            nav: false,
            autoplay: true,
            autoplayTimeout: 4500,
            autoplayHoverPause: true,
            smartSpeed: 600,
            autoHeight: false,
            responsive: {
                0:   { items: 1 },
                768: { items: 2 },
                992: { items: 3 }
            }
        });
    }

    if (window.whenVendor) {
        whenVendor('owl', initClinicsSlider);
    } else {
        $(document).ready(initClinicsSlider);
    }
})(jQuery);
