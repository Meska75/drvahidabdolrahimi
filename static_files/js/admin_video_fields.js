(function ($) {
    'use strict';

    function toggleVideoFields() {
        var val = $('#id_source_type').val();
        if (val === 'upload') {
            $('.field-file_path, .field-platform').show();
            $('.field-embed_code').hide();
        } else {
            /* حالت iframe خارجی */
            $('.field-file_path').hide();
            $('.field-embed_code, .field-platform').show();
        }
    }

    $(document).ready(function () {
        toggleVideoFields();
        $('#id_source_type').on('change', toggleVideoFields);
    });

}(django.jQuery));
