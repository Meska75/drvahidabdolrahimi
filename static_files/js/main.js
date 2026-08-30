(function($) {
    "use strict"
    jQuery(document).ready(function() {

        var headerTopEl = document.querySelector('.header-top');
        var mobileBarEl = document.getElementById('mobileContactBar');
        var layoutRaf = null;

        // هم‌ترازی #header با ارتفاع واقعی نوار بالا (رفع فاصله خالی هنگام اسکرول)
        function syncHeaderLayout() {
            var $headerTop = $('.header-top');
            var $header = $('#header');
            if ($(window).width() >= 992 && $headerTop.length && $headerTop.is(':visible')) {
                var topH = $headerTop.outerHeight() || 0;
                document.documentElement.style.setProperty('--header-top-live', topH + 'px');
                var total = topH + ($header.outerHeight() || 0);
                document.documentElement.style.setProperty('--site-header-offset', total + 'px');
            } else {
                document.documentElement.style.removeProperty('--header-top-live');
                document.documentElement.style.removeProperty('--site-header-offset');
            }
        }

        function syncMobileHeaderOffset() {
            var headerEl = document.getElementById('header');
            var logoEl = document.getElementById('logo');
            var rowEl = headerEl ? headerEl.querySelector('.container > .row') : null;
            if ($(window).width() > 991 || !headerEl) {
                document.documentElement.style.removeProperty('--mobile-header-offset');
                document.documentElement.style.removeProperty('--mobile-header-bar-h');
                document.documentElement.style.removeProperty('--mobile-hero-content-offset');
                return;
            }
            var headerRect = headerEl.getBoundingClientRect();
            var barRect = rowEl ? rowEl.getBoundingClientRect() : headerRect;
            var barH = Math.ceil(barRect.height);
            document.documentElement.style.setProperty('--mobile-header-bar-h', barH + 'px');

            var logoBottom = logoEl
                ? Math.ceil(logoEl.getBoundingClientRect().bottom - headerRect.top)
                : barH;
            var totalH = Math.max(barH, logoBottom);
            document.documentElement.style.setProperty('--mobile-header-offset', totalH + 'px');
            document.documentElement.style.setProperty(
                '--mobile-hero-content-offset',
                (logoBottom + 12) + 'px'
            );
        }

        function syncMobileBottomBar() {
            if (!mobileBarEl || $(window).width() > 991) {
                mobileBarEl && (mobileBarEl.style.bottom = '');
                document.documentElement.style.setProperty('--mobile-bottom-bar-h', '0px');
                return;
            }
            mobileBarEl.style.bottom = '0';
            var rect = mobileBarEl.getBoundingClientRect();
            var gap = Math.max(0, window.innerHeight - rect.bottom);
            if (gap > 0 && gap < 8) {
                mobileBarEl.style.bottom = (-Math.ceil(gap)) + 'px';
            }
            document.documentElement.style.setProperty(
                '--mobile-bottom-bar-h',
                Math.ceil(rect.height + gap) + 'px'
            );
        }

        // آیکون منوی موبایل بر اساس URL
        function getMobileNavIcon(href, text) {
            var target = (href + ' ' + text).toLowerCase();
            if (/contact|تماس|اتصل|contact-us/.test(target)) return 'fa-map-marker';
            if (/about|درباره|حول|about-doctor/.test(target)) return 'fa-user-md';
            if (/office|مطب|clinic/.test(target)) return 'fa-stethoscope';
            if (/surgery|جراح|جراحی/.test(target)) return 'fa-heartbeat';
            if (/services|خدمات|خدمات|services-overview/.test(target)) return 'fa-medkit';
            if (/blog|مقالات|مقال|articles/.test(target)) return 'fa-newspaper-o';
            if (/gallery|گالری|معرض|album/.test(target)) return 'fa-image';
            if (/video|ویدیو|فيديو|videos/.test(target)) return 'fa-play-circle';
            if (/\/$|home|خانه|الرئيسية|english_home|arabic_home|persian_home/.test(target)) return 'fa-home';
            return 'fa-circle-o';
        }

        function getMobileNavLabels() {
            var lang = document.documentElement.lang || 'fa';
            if (lang === 'en') {
                return { title: 'Menu', sub: 'Dr. Vahid Abdolrahimi', expand: 'Expand submenu' };
            }
            if (lang === 'ar') {
                return { title: 'القائمة', sub: 'د. وحيد عبد الرحيمي', expand: 'فتح القائمة الفرعية' };
            }
            return { title: 'منو', sub: 'دکتر وحید عبدالرحیمی', expand: 'باز کردن زیرمنو' };
        }

        function isRtlNav() {
            var dir = (document.documentElement.getAttribute('dir') || '').toLowerCase();
            if (dir === 'rtl') return true;
            if (dir === 'ltr') return false;
            var lang = (document.documentElement.getAttribute('lang') || '').toLowerCase();
            return lang === 'fa' || lang === 'ar';
        }

        function scheduleLayoutSync() {
            if (layoutRaf) {
                cancelAnimationFrame(layoutRaf);
            }
            layoutRaf = requestAnimationFrame(function() {
                layoutRaf = null;
                syncHeaderLayout();
                syncMobileHeaderOffset();
                syncMobileBottomBar();
            });
        }

        // فاصله اسکرول نرم — نوار بالا + منو در دسکتاپ
        function getHeaderOffset() {
            if ($(window).width() <= 991) {
                var mobileOffset = parseInt(
                    getComputedStyle(document.documentElement).getPropertyValue('--mobile-header-offset'),
                    10
                );
                if (mobileOffset) {
                    return mobileOffset;
                }
            }
            var offset = $('#header').outerHeight() || 0;
            if ($(window).width() >= 992 && $('.header-top').length && $('.header-top').is(':visible')) {
                offset += $('.header-top').outerHeight() || 0;
            }
            return offset;
        }

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
            $('#mobile-nav, #mobile-nav-toggle, #mobile-body-overly').remove();

            var $mobile_nav = $('#nav-menu-container').clone().prop({
                id: 'mobile-nav'
            });
            $mobile_nav.children('ul').attr({
                'class': '',
                'id': ''
            });

            // سرصفحه و آیکون‌های منو
            var navLabels = getMobileNavLabels();
            $mobile_nav.prepend(
                '<div class="mobile-nav-head">' +
                '<span class="mobile-nav-head-title">' + navLabels.title + '</span>' +
                '<span class="mobile-nav-head-sub">' + navLabels.sub + '</span>' +
                '</div>'
            );
            $mobile_nav.children('ul').children('li').children('a').each(function() {
                var $link = $(this);
                if ($link.find('.mobile-nav-icon').length) return;
                var href = $link.attr('href') || '';
                var text = $link.text().trim();
                var icon = getMobileNavIcon(href, text);
                $link.prepend('<i class="fa ' + icon + ' mobile-nav-icon" aria-hidden="true"></i>');
            });
            // متن لینک داخل span تا زیر آیکون نرود
            $mobile_nav.children('ul').children('li').children('a').each(function() {
                var $link = $(this);
                if ($link.find('.mobile-nav-label').length) return;
                var text = $link.clone().children().remove().end().text().trim();
                $link.contents().filter(function() {
                    return this.nodeType === 3;
                }).remove();
                $link.append('<span class="mobile-nav-label">' + text + '</span>');
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
            // آدرس کامل تماس در پایین منوی همبرگر
            var $contactSource = $('.mobile-nav-contact-source');
            if ($contactSource.length) {
                $mobile_nav.append($contactSource.children().clone());
            }
            // آیتم‌های دارای زیرمنو
            $mobile_nav.find('li').filter(function() {
                return $(this).children('ul').length > 0;
            }).each(function() {
                var $li = $(this);
                var rtl = isRtlNav();
                $li.addClass('menu-has-children');
                $li.children('.mobile-nav-sub-toggle').remove();
                $li.children('.mobile-nav-row').remove();

                var $a = $li.children('a').first();
                if (!$a.length) return;

                // ترتیب داخل لینک: آیکون سپس متن — direction ردیف آیکون را به ابتدای خواندن می‌برد
                var $icon = $a.find('.mobile-nav-icon').detach();
                var $label = $a.find('.mobile-nav-label').detach();
                $a.empty().append($icon).append($label);

                // فلش CSS — بدون Font Awesome تا مربع خالی دیده نشود
                var $toggle = $(
                    '<button type="button" class="mobile-nav-sub-toggle" aria-expanded="false" aria-label="' + navLabels.expand + '">' +
                    '<span class="mobile-nav-chevron" aria-hidden="true"></span></button>'
                );
                var $row = $('<div class="mobile-nav-row' + (rtl ? ' mobile-nav-row--rtl' : ' mobile-nav-row--ltr') + '"></div>');
                $row.append($a).append($toggle);
                $li.prepend($row);
            });

            $('body').append($mobile_nav);
            $('body').prepend('<button type="button" id="mobile-nav-toggle" aria-label="Menu" aria-expanded="false"><i class="fa fa-bars" aria-hidden="true"></i></button>');
            $('body').append('<div id="mobile-body-overly"></div>');

            $(document).on('click', '#mobile-nav .mobile-nav-sub-toggle', function(e) {
                e.preventDefault();
                e.stopPropagation();
                var $btn = $(this);
                var $li = $btn.closest('.menu-has-children');
                var $sub = $li.children('ul').first();
                var isOpen = $sub.is(':visible');
                $sub.stop(true, true).slideToggle(200);
                $sub.toggleClass('menu-item-active');
                $btn.attr('aria-expanded', String(!isOpen));
                $btn.toggleClass('is-open', !isOpen);
                $li.toggleClass('submenu-open', !isOpen);
            });

            // بستن زیرمنو با کلیک روی لینک «خدمات» وقتی باز است
            $(document).on('click', '#mobile-nav .menu-has-children > .mobile-nav-row > a', function(e) {
                var $li = $(this).closest('.menu-has-children');
                var $sub = $li.children('ul').first();
                if (!$sub.is(':visible')) return;
                e.preventDefault();
                $sub.stop(true, true).slideUp(200);
                $sub.removeClass('menu-item-active');
                $li.removeClass('submenu-open');
                $li.find('.mobile-nav-sub-toggle').attr('aria-expanded', 'false').removeClass('is-open');
            });

            function resetMobileSubmenus() {
                $('#mobile-nav .menu-has-children').removeClass('submenu-open');
                $('#mobile-nav .menu-has-children > ul').stop(true, true).hide().removeClass('menu-item-active');
                $('#mobile-nav .mobile-nav-sub-toggle').attr('aria-expanded', 'false').removeClass('is-open');
            }

            $(document).on('click', '#mobile-nav-toggle', function(e) {
                var isOpen = !$('body').hasClass('mobile-nav-active');
                $('body').toggleClass('mobile-nav-active');
                $('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
                $('#mobile-nav-toggle').attr('aria-expanded', String(isOpen));
                $('#mobile-body-overly').toggle();
                if (!isOpen) resetMobileSubmenus();
            });

            $(document).click(function(e) {
                var container = $("#mobile-nav, #mobile-nav-toggle");
                if (!container.is(e.target) && container.has(e.target).length === 0) {
                    if ($('body').hasClass('mobile-nav-active')) {
                        $('body').removeClass('mobile-nav-active');
                        $('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
                        $('#mobile-nav-toggle').attr('aria-expanded', 'false');
                        $('#mobile-body-overly').fadeOut();
                        resetMobileSubmenus();
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
                        top_space = getHeaderOffset();
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
                        $('#mobile-nav .menu-has-children').removeClass('submenu-open');
                        $('#mobile-nav .menu-has-children > ul').hide().removeClass('menu-item-active');
                        $('#mobile-nav .mobile-nav-sub-toggle').attr('aria-expanded', 'false').removeClass('is-open');
                    }
                    return false;
                }
            }
        });

        // هدر اسکرول — دسکتاپ: نوار بالا جمع می‌شود ولی پنهان نمی‌شود
        $(window).on('scroll', function() {
            var scrolled = $(this).scrollTop() > 80;
            if (scrolled) {
                $('#header').addClass('header-scrolled');
                $('.header-top').addClass('header-scrolled');
            } else {
                $('#header').removeClass('header-scrolled');
                $('.header-top').removeClass('header-scrolled');
            }
            scheduleLayoutSync();
        });

        if (headerTopEl && window.ResizeObserver) {
            var headerObserver = new ResizeObserver(scheduleLayoutSync);
            headerObserver.observe(headerTopEl);
        }

        var headerMainEl = document.getElementById('header');
        if (headerMainEl && window.ResizeObserver) {
            var headerMainObserver = new ResizeObserver(scheduleLayoutSync);
            headerMainObserver.observe(headerMainEl);
        }

        if (mobileBarEl && window.ResizeObserver) {
            var mobileBarObserver = new ResizeObserver(scheduleLayoutSync);
            mobileBarObserver.observe(mobileBarEl);
        }

        scheduleLayoutSync();
        $(window).on('resize load', scheduleLayoutSync);

    });
})(jQuery);
