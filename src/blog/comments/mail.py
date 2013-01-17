#!/usr/bin/env python

import sys, smtplib

if len(sys.argv) != 2 or not len(sys.argv[1]):
	sys.exit(1)

article = sys.argv[1]
shortArticle = article
if len(shortArticle) > 64:
	shortArticle = shortArticle[:64] + '...'
address = 'perot.me-comment-' + shortArticle + '@perot.me'

# Could use SMTP_SSL but this is all local traffic
server = smtplib.SMTP('localhost')
server.sendmail(
	address,
	address,
	'\r\n'.join((
		'From: ' + address,
		'To: ' + address,
		'Subject: [perot.me] ' + article + ': New comment notification',
		'',
		'There are new comments waiting on article ' + article + ':',
		'',
		'https://perot.me/' + article
	))
)
server.quit()
