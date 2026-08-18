/* لود تنبل کتابخانه‌های غیرحیاتی — Owl، Swiper، Leaflet، WOW
   فقط وقتی بخش مربوطه نزدیک viewport باشد دانلود می‌شود */
(function () {
    'use strict';

    var loaded = {};
    var ready = {};
    var callbacks = {};

    window.whenVendor = function (name, fn) {
        if (ready[name]) {
            fn();
            return;
        }
        (callbacks[name] = callbacks[name] || []).push(fn);
    };

    function markReady(name) {
        if (ready[name]) return;
        ready[name] = true;
        (callbacks[name] || []).forEach(function (fn) {
            try { fn(); } catch (e) { /* ignore */ }
        });
        callbacks[name] = [];
    }

    function loadCss(href) {
        if (!href || loaded[href]) return Promise.resolve();
        loaded[href] = true;
        return new Promise(function (resolve) {
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = resolve;
            document.head.appendChild(link);
        });
    }

    function loadJs(src) {
        if (!src || loaded[src]) return Promise.resolve();
        loaded[src] = true;
        return new Promise(function (resolve) {
            var script = document.createElement('script');
            script.src = src;
            script.async = true;
            script.onload = resolve;
            script.onerror = resolve;
            document.body.appendChild(script);
        });
    }

    function whenVisible(selector, onVisible, rootMargin) {
        var el = document.querySelector(selector);
        if (!el) return;
        var ran = false;
        function run() {
            if (ran) return;
            ran = true;
            onVisible();
        }
        if (!('IntersectionObserver' in window)) {
            run();
            return;
        }
        var io = new IntersectionObserver(function (entries) {
            for (var i = 0; i < entries.length; i++) {
                if (entries[i].isIntersecting) {
                    io.disconnect();
                    run();
                    break;
                }
            }
        }, { rootMargin: rootMargin || '280px 0px' });
        io.observe(el);
    }

    function boot() {
        var v = window.LAZY_VENDORS || {};

        whenVisible('.owl-carousel', function () {
            Promise.all([loadCss(v.owlCss), loadJs(v.owlJs)]).then(function () {
                markReady('owl');
            });
        });

        whenVisible('.tst-swiper', function () {
            Promise.all([loadCss(v.swiperCss), loadJs(v.swiperJs)]).then(function () {
                markReady('swiper');
            });
        });

        whenVisible('#neshanMap, #neshanMapContact', function () {
            Promise.all([loadCss(v.leafletCss), loadJs(v.leafletJs)]).then(function () {
                markReady('leaflet');
            });
        });

        whenVisible('.wow', function () {
            Promise.all([loadCss(v.animateCss), loadJs(v.wowJs)]).then(function () {
                if (typeof WOW !== 'undefined') {
                    new WOW().init();
                }
                markReady('wow');
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
