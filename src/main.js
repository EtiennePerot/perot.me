import('http://code.jquery.com/jquery.min.js');

pgpWidget = {
	init: function() {
		$('.pgp-fingerprint').attr('wrap', 'off').click(function(){
			$(this).select();
		});
	}
};
$(pgpWidget.init);