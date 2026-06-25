(function($) {
    "use strict"
    jQuery(document).ready(function() {

        // Initiate superfish on nav menu
        $('.nav-menu').superfish({
            animation: {
            opacity: 'show'
            },
            speed: 400
        });

        // Mobile Navigation
        if ($('#nav-menu-container').length) {
            var $mobile_nav = $('#nav-menu-container').clone().prop({
            id: 'mobile-nav'
            });
            $mobile_nav.find('> ul').attr({
            'class': '',
            'id': ''
            });
            // آیکون‌های شبکه اجتماعی — پویا از هدر دسکتاپ (تغییر از ادمین پنل اعمال می‌شود)
            var $socialLinks = $('.social-links a');
            if ($socialLinks.length) {
                var socialHtml = '<div class="mobile-nav-social">';
                $socialLinks.each(function() {
                    socialHtml += '<a href="' + $(this).attr('href') + '" target="_blank" rel="noopener" aria-label="' + $(this).attr('aria-label') + '">' + $(this).html() + '</a>';
                });
                socialHtml += '</div>';
                $mobile_nav.append(socialHtml);
            }
            $('body').append($mobile_nav);
            $('body').prepend('<button type="button" id="mobile-nav-toggle"><i class="lnr lnr-menu"></i></button>');
            $('body').append('<div id="mobile-body-overly"></div>');
            $('#mobile-nav').find('.menu-has-children').prepend('<i class="lnr lnr-chevron-down"></i>');

            $(document).on('click', '.menu-has-children i', function(e) {
            $(this).next().toggleClass('menu-item-active');
            $(this).nextAll('ul').eq(0).slideToggle();
            $(this).toggleClass("lnr-chevron-up lnr-chevron-down");
            });

            $(document).on('click', '#mobile-nav-toggle', function(e) {
            $('body').toggleClass('mobile-nav-active');
            $('#mobile-nav-toggle i').toggleClass('lnr-cross lnr-menu');
            $('#mobile-body-overly').toggle();
            });

            $(document).click(function(e) {
            var container = $("#mobile-nav, #mobile-nav-toggle");
            if (!container.is(e.target) && container.has(e.target).length === 0) {
                if ($('body').hasClass('mobile-nav-active')) {
                $('body').removeClass('mobile-nav-active');
                $('#mobile-nav-toggle i').toggleClass('lnr-cross lnr-menu');
                $('#mobile-body-overly').fadeOut();
                }
            }
            });
        } else if ($("#mobile-nav, #mobile-nav-toggle").length) {
            $("#mobile-nav, #mobile-nav-toggle").hide();
        }

        // Smooth scroll for the menu and links with .scrollto classes
        $('.nav-menu a, #mobile-nav a, .scrollto').on('click', function() {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            if (target.length) {
                var top_space = 0;

                if ($('#header').length) {
                top_space = $('#header').outerHeight();

                if( ! $('#header').hasClass('header-fixed') ) {
                    top_space = top_space;
                }
                }

                $('html, body').animate({
                scrollTop: target.offset().top - top_space
                }, 1500, 'easeInOutExpo');

                if ($(this).parents('.nav-menu').length) {
                $('.nav-menu .menu-active').removeClass('menu-active');
                $(this).closest('li').addClass('menu-active');
                }

                if ($('body').hasClass('mobile-nav-active')) {
                $('body').removeClass('mobile-nav-active');
                $('#mobile-nav-toggle i').toggleClass('lnr-times lnr-bars');
                $('#mobile-body-overly').fadeOut();
                }
                return false;
            }
            }
        });



        // هدر اسکرول — وقتی بیشتر از ۸۰px اسکرول شد، header-top پنهان و #header بالا میاد
        $(window).scroll(function() {
            if ($(this).scrollTop() > 80) {
                $('#header').addClass('header-scrolled');
                $('.header-top').addClass('header-scrolled');
            } else {
                $('#header').removeClass('header-scrolled');
                $('.header-top').removeClass('header-scrolled');
            }
        });


        // Department Slider
        $('.department-slider').owlCarousel({
            loop: true,
            margin: 10,
            autoplay: true,
            autoplayTimeout: 2000,
            autoplayHoverPause: true,
            nav: false,
            dots: true,
            smartSpeed: 1000,
            responsiveClass: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 1
                },
                768: {
                    items: 2
                },
                992: {
                    items: 3
                }
            }
        });

        // کاروسل تیم مطب — صفحه اصلی و صفحه خدمات (۲ نفر در موبایل، چرخش خودکار، قابل کشیدن)
        if ($('.team-carousel').length) {
            $('.team-carousel').owlCarousel({
                loop: true,
                margin: 24,
                autoplay: true,
                autoplayTimeout: 3500,
                autoplayHoverPause: true,
                nav: false,
                dots: true,
                smartSpeed: 800,
                responsiveClass: true,
                responsive: {
                    0:   { items: 2 },
                    768: { items: 3 },
                    992: { items: 4 }
                }
            });
        }

        // Date Picker
        jQuery('#datepicker').datetimepicker({
            timepicker:false,
            format:'d.m.Y',
        });

        // // Nice Select
        $('select').niceSelect();
        


    });

    jQuery(window).on('load', function() {
        // WOW JS
        new WOW().init();
        // Preloader
		$('.preloader').fadeOut(500);
    });
})(jQuery);
