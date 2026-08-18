(function($) {
    "use strict"
    jQuery(document).ready(function() {

        // منوی دسکتاپ — Superfish
        if ($.fn.superfish && $('.nav-menu').length) {
            $('.nav-menu').superfish({
                animation: {
                    opacity: 'show'
                },
                speed: 400
            });
        }

        // منوی موبایل — آیکون‌ها از Font Awesome (بدون Linearicons)
        if ($('#nav-menu-container').length) {
            var $mobile_nav = $('#nav-menu-container').clone().prop({
                id: 'mobile-nav'
            });
            $mobile_nav.find('> ul').attr({
                'class': '',
                'id': ''
            });
            // آیکون‌های شبکه اجتماعی — پویا از هدر دسکتاپ
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
            $('body').prepend('<button type="button" id="mobile-nav-toggle" aria-label="Menu" aria-expanded="false"><i class="fa fa-bars" aria-hidden="true"></i></button>');
            $('body').append('<div id="mobile-body-overly"></div>');
            $('#mobile-nav').find('.menu-has-children').prepend('<i class="fa fa-chevron-down" aria-hidden="true"></i>');

            $(document).on('click', '.menu-has-children i', function(e) {
                $(this).next().toggleClass('menu-item-active');
                $(this).nextAll('ul').eq(0).slideToggle();
                $(this).toggleClass("fa-chevron-up fa-chevron-down");
            });

            $(document).on('click', '#mobile-nav-toggle', function(e) {
                var isOpen = !$('body').hasClass('mobile-nav-active');
                $('body').toggleClass('mobile-nav-active');
                $('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
                $('#mobile-nav-toggle').attr('aria-expanded', String(isOpen));
                $('#mobile-body-overly').toggle();
            });

            $(document).click(function(e) {
                var container = $("#mobile-nav, #mobile-nav-toggle");
                if (!container.is(e.target) && container.has(e.target).length === 0) {
                    if ($('body').hasClass('mobile-nav-active')) {
                        $('body').removeClass('mobile-nav-active');
                        $('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
                        $('#mobile-nav-toggle').attr('aria-expanded', 'false');
                        $('#mobile-body-overly').fadeOut();
                    }
                }
            });
        } else if ($("#mobile-nav, #mobile-nav-toggle").length) {
            $("#mobile-nav, #mobile-nav-toggle").hide();
        }

        // اسکرول نرم برای لینک‌های داخلی منو
        $('.nav-menu a, #mobile-nav a, .scrollto').on('click', function() {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
                var target = $(this.hash);
                if (target.length) {
                    var top_space = 0;

                    if ($('#header').length) {
                        top_space = $('#header').outerHeight();
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
                        $('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
                        $('#mobile-nav-toggle').attr('aria-expanded', 'false');
                        $('#mobile-body-overly').fadeOut();
                    }
                    return false;
                }
            }
        });

        // هدر اسکرول — وقتی بیشتر از ۸۰px اسکرول شد، header-top پنهان و #header بالا می‌آید
        $(window).scroll(function() {
            if ($(this).scrollTop() > 80) {
                $('#header').addClass('header-scrolled');
                $('.header-top').addClass('header-scrolled');
            } else {
                $('#header').removeClass('header-scrolled');
                $('.header-top').removeClass('header-scrolled');
            }
        });

    });
})(jQuery);
