'use strict';
(function($){
    $('body').on('click', '.js-wbquickview-link', e => {
        e.preventDefault();
        const $currentTarget = $(e.currentTarget);
        var product_url = $currentTarget.data('url');
        var variant_id = $currentTarget.attr('variant-id');
        if (product_url.indexOf("?") > 0) {
            var product_url = product_url.substring(0, product_url.indexOf("?"));
        }
        $.ajax({
            url: product_url + '?view=wbquickview' + ((typeof variant_id !== 'undefined') ? '&variant=' + variant_id : ''),
            success: function(data) {
                if (!data) { return; }
                const html = $(data).find('[data-html="content"]').html();
                $('.js-wbquickview').html(html);
                $.magnificPopup.open({
                    preloader: true,
                    tLoading: '',
                    items: {
                        src: '<div id="wbquickview" class="js-wbquickview white-popup">'+ html +'</div>',
                        type: 'inline'
                    },
                    closeBtnInside: true
                });
                if (e.keyCode == 27) { //Escape button
                    $.magnificPopup.close();
                }
               
            }
        });
    });
})(jQuery);
