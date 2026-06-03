(function ($) {
    "use strict";
    $(document).ready(function () {

        // اسلایدر مراکز درمانی — RTL، سه کارت در دسکتاپ
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
            responsive: {
                0:   { items: 1 },
                768: { items: 2 },
                992: { items: 3 }
            }
        });

    });
})(jQuery);
