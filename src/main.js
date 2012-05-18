import('http://code.jquery.com/jquery.min.js');

emailReplace = {
	init: function() {
		$('.email-replace').each(function() {
			$(this).text($(this).text().replace(/(\S+)\s+at\s+(\S+)\s+dot\s+(\S+)/gi, '$1@$2.$3')).wrapInner('<a href="mailto:' + $(this).text() + '"/>');
		});
	}
};
$(emailReplace.init);