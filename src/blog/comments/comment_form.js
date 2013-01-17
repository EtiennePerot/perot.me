commentform = {
	statusNode: null,
	submitNode: null,
	articleNode: null,
	nonceNode: null,
	messageNode: null,
	usernameNode: null,
	websiteNode: null,
	websiteLine: null,
	formControls: null,
	init: function() {
		commentform.statusNode = $('#comment-status');
		commentform.submitNode = $('#comment-submit');
		commentform.articleNode = $('#comment-article');
		commentform.nonceNode = $('#comment-nonce');
		commentform.messageNode = $('#comment-message');
		commentform.usernameNode = $('#comment-username');
		commentform.websiteNode = $('#comment-website');
		commentform.websiteLine = $('.author-website');
		commentform.formControls = $([commentform.messageNode, commentform.usernameNode, commentform.websiteNode, commentform.submitNode]);
		commentform.usernameNode.change(commentform.authorUpdated).keyup(commentform.authorUpdated);
		commentform.authorUpdated();
		$('#comment-form').submit(commentform.submitForm);
		commentform.submitNode.click(commentform.submitForm);
	},
	authorUpdated: function() {
		if(commentform.usernameNode.val() && commentform.usernameNode.val().toLowerCase() != 'anonymous') {
			commentform.websiteLine.fadeIn('fast');
		} else {
			commentform.websiteLine.fadeOut('fast');
		}
	},
	cacheBust: function() {
		return (Math.random().toString() + Math.random().toString() + Math.random().toString()).replace(/\./g, '');
	},
	updateForm: function(statusClass, statusText, reportError) {
		commentform.statusNode.text('').removeClass('comment-ajax comment-error comment-success').addClass('comment-' + statusClass).text(statusText);
		if(statusClass == 'error' && reportError) {
			commentform.statusNode.html(commentform.statusNode.html() + '<br/>Please report this to me (contact information available in the sidebar).');
		}
		if(statusClass == 'ajax') {
			commentform.formControls.attr('disabled', 'true');
		} else {
			commentform.formControls.removeAttr('disabled');
			commentform.nonceNode.val('');
		}
	},
	ajaxError: function(errorContext, textStatus, errorThrown) {
		textStatus = textStatus ? textStatus : '[Unknown status]';
		errorThrown = errorThrown ? errorThrown : '[Unknown error]';
		commentform.updateForm('error', 'Error ' + errorContext + ' (' + textStatus + ': ' + errorThrown + ').', true);
	},
	submitForm: function() {
		$.ajax({
			beforeSend: function() {
				commentform.updateForm('ajax', 'Acquiring nonce...', false);
			},
			cache: false,
			data: {
				'json': '1',
				'article': commentform.articleNode.val()
			},
			dataType: 'json',
			error: function(jqXHR, textStatus, errorThrown) {
				commentform.ajaxError('acquiring nonce', textStatus, errorThrown);
			},
			success: function(data, textStatus, jqXHR) {
				if('error' in data) {
					commentform.updateForm('error', 'Error acquiring nonce (' + data['error'] + ').', true);
				} else if('nonce' in data) {
					commentform.nonceGrabbed(data['nonce']);
				} else {
					commentform.updateForm('error', 'Error acquiring nonce (No data received).', true);
				}
			},
			type: 'POST',
			url: '/getnonce?cachebust=' + commentform.cacheBust()
		});
		return false;
	},
	nonceGrabbed: function(nonce) {
		commentform.nonceNode.val(nonce);
		$.ajax({
			beforeSend: function() {
				commentform.updateForm('ajax', 'Submitting comment...', false);
			},
			cache: false,
			data: {
				'json': '1',
				'article': commentform.articleNode.val(),
				'nonce': commentform.nonceNode.val(),
				'message': commentform.messageNode.val(),
				'username': commentform.usernameNode.val(),
				'website': commentform.websiteNode.val()
			},
			dataType: 'json',
			error: function(jqXHR, textStatus, errorThrown) {
				commentform.ajaxError('submitting comment', textStatus, errorThrown);
			},
			success: function(data, textStatus, jqXHR) {
				if('error' in data) {
					commentform.updateForm('error', 'Error submitting comment (' + data['error'] + ').', false);
				} else if('success' in data) {
					commentform.updateForm('success', data['success'], false);
					commentform.resetForm();
				} else {
					commentform.updateForm('error', 'Error submitting comment (No data received).', true);
				}
			},
			type: 'POST',
			url: '/comment?cachebust=' + commentform.cacheBust()
		});
	},
	resetForm: function() {
		commentform.messageNode.val('').focus();
	}
}
$(commentform.init);