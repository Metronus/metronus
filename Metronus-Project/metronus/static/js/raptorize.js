function showRaptor() {
    (function ($) {
        var raptorUrls = [
            '/static/img/raptors/raptor0.png',
            '/static/img/raptors/raptor1.png',
            '/static/img/raptors/raptor2.png',
            '/static/img/raptors/raptor3.png',
            '/static/img/raptors/raptor4.png',
            '/static/img/raptors/raptor5.png',
            '/static/img/raptors/raptor6.png',
            '/static/img/raptors/raptor7.png',
            '/static/img/raptors/raptor8.png',
            '/static/img/raptors/raptor9.png'
        ];
        var raptorCounter = 0;

        $.fn.raptorize = function (options) {

            var randomImageUrl = raptorUrls[Math.floor(Math.random() * raptorUrls.length)];
            var defaults = {
                enterOn: 'timer',
                delayTime: 100
            };

            //Extend those options
            var options = $.extend(defaults, options);

            return this.each(function () {

                var _this = $(this);
                var audioSupported = false;

                $("#elRaptor").remove();
                var raptorImageMarkup = '<img style="display: none;z-index:30000" src="' + randomImageUrl + '" />';
                var locked = false;
                var raptor = $(raptorImageMarkup);
                $('body').append(raptor);
                raptor.css({
                    "position": "fixed",
                    "bottom": "-310px",
                    "right": "0",
                    "display": "block"
                })

                init();

                function init() {
                    var image = new Image();
                    image.onload = function () { initAfterImageLoad() };
                    image.src = randomImageUrl;
                }

                function initAfterImageLoad() {
                    locked = true;

                    raptor.animate({
                        "bottom": "0"
                    }, function () {

                        $(this).animate({
                            "bottom": "-20px"
                        }, 100, function () {
                            var offset = (($(this).position().left) + 400);
                            $(this).delay(300).animate({
                                "right": offset
                            }, 2200, function () {
                                raptor.remove();
                                locked = false;
                            })
                        });
                    });
                }


            });
        }
    })(jQuery);

    $("body").raptorize();
    $(window).scrollTop(9999999);
}

$(function () {
    var code1 = String.fromCharCode(38, 38, 40, 40, 37, 39, 37, 39, 66, 65);
    var codeBuffer = "";
    $(document).keyup(function (e) {
        codeBuffer += String.fromCharCode(e.which);
        if (code1.substring(0, codeBuffer.length) == codeBuffer) {
            if (code1.length == codeBuffer.length) {
                toggle1();
                codeBuffer = String.fromCharCode(38, 38, 40, 40, 37, 39, 37, 39, 66);
            }
        } else {
            codeBuffer = "";
        }
    });

    function toggle1() {
        var $body = $("body");
        if ($body.raptorize) {
            $body.raptorize();
        } else {
            showRaptor();
        }
    }
});
