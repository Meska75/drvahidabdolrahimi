(function ($) {
    'use strict';

    /* ---- فیلتر دسته‌بندی ---- */
    $(document).on('click', '.filter-btn[data-category]', function () {
        var cat = $(this).data('category');
        $('.filter-btn[data-category]').removeClass('is-checked');
        $(this).addClass('is-checked');

        if (cat === 'all') {
            $('.video-card-wrap').removeClass('v-hidden');
        } else {
            $('.video-card-wrap').addClass('v-hidden');
            $('.video-card-wrap[data-category="' + cat + '"]').removeClass('v-hidden');
        }
    });

    /* ---- مودال ویدیو ---- */
    function buildPlayer(sourceType, fileUrl, embedCode) {
        if (sourceType === 'upload' && fileUrl) {
            return '<video controls autoplay style="width:100%;height:100%;position:absolute;inset:0;">' +
                   '<source src="' + fileUrl + '"></video>';
        }
        if (embedCode) {
            return embedCode;
        }
        return '<div style="color:rgba(255,255,255,.4);display:flex;align-items:center;' +
               'justify-content:center;height:100%;font-size:.9rem;">منبع ویدیو تعریف نشده</div>';
    }

    function openVM($card) {
        var sourceType = $card.data('source-type');
        var fileUrl    = $card.data('file-url') || '';
        var embedCode  = $card.data('embed-code') || '';

        $('#vm-player').html(buildPlayer(sourceType, fileUrl, embedCode));
        $('#vm-title').text($card.data('title') || '');
        $('#vm-desc').text($card.data('desc') || '');
        $('#vm-cat').text($card.find('.video-cat-badge').text().trim());

        $('#vm-overlay').addClass('vm-active');
        $('body').css('overflow', 'hidden');
    }

    function closeVM() {
        $('#vm-overlay').removeClass('vm-active');
        $('#vm-player').html('');
        $('body').css('overflow', '');
    }

    $(document).on('click', '.video-card', function () {
        openVM($(this));
    });

    $('#vm-close').on('click', closeVM);
    $('#vm-overlay').on('click', function (e) {
        if (e.target === this) closeVM();
    });
    $(document).on('keydown', function (e) {
        if (e.key === 'Escape') closeVM();
    });

}(jQuery));
