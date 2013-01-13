js_import('http://code.jquery.com/jquery.min.js');

emailReplace = {
	init: function() {
		$('.email-replace').each(function() {
			var email = $(this).text().replace(/^\s+|\s+$/g, '');
			var label = null;
			if(email.indexOf('<') != -1 && email.indexOf('>') != -1) {
				label = email.substring(0, email.indexOf('<')).replace(/^\s+|\s+$/g, '');
				email = email.substring(email.indexOf('<') + 1, email.indexOf('>')).replace(/^\s+|\s+$/g, '');
			}
			email = email.replace(/\s*\(?dot\)?\s*/gi, '.').replace(/\s*\(?at\)?\s*/gi, '@');
			if(label == null) {
				label = email;
			}
			$(this).empty().append($('<a/>').attr('href', 'mailto:' + email).text(label));
		});
	}
};
$(emailReplace.init);

javascriptOnly = {
	init: function() {
		$('.javascript-only').css('display', 'block');
	}
}
$(javascriptOnly.init);
