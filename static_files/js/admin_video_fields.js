(function ($) {
    'use strict';

    var VIDEO_ACCEPT = 'video/mp4,video/webm,video/ogg,video/quicktime,.mp4,.webm,.ogg,.mov,.avi,.mkv,.m4v';

    function toggleVideoFields() {
        var val = $('#id_source_type').val();
        if (val === 'upload') {
            $('.field-file_path, .field-platform').show();
            $('.field-embed_code').hide();
            /* اطمینان از فیلتر ویدیو روی input فایل */
            $('#id_file_path').attr('accept', VIDEO_ACCEPT);
        } else {
            /* حالت iframe خارجی */
            $('.field-file_path').hide();
            $('.field-embed_code, .field-platform').show();
        }
    }

    $(document).ready(function () {
        /* تصویر بند انگشتی فقط عکس باشد */
        $('#id_thumbnail').attr('accept', 'image/*');
        $('#id_file_path').attr('accept', VIDEO_ACCEPT);
        toggleVideoFields();
        $('#id_source_type').on('change', toggleVideoFields);
    });

}(django.jQuery));
