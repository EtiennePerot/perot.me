#!/usr/bin/env python3

# Usage: nav.py section-name [breadcrumb-url breadcrumb-label]

import sys, html

# Navigation links
navLinks = [
	{
		'name': 'blog',
		'label': 'Blog',
		'url': '/',
		'extra': '<a href="/posts.atom"><span class="icon-rss"></span></a>'
	},
	{
		'name': 'projects',
		'label': 'Projects',
		'url': '/projects'
	},
	{
		'name': 'about',
		'label': 'About',
		'url': '/about'
	},
	{
		'name': 'resume',
		'label': 'CV',
		'url': '/cv'
	}
]

def navLink(l):
	isCurrent = ''
	if sys.argv[1] == l['name']:
		isCurrent = ' class="current"'
	print('<li><a href="' + l['url'] + '"' + isCurrent + '>' + l['label'] + '</a>', end='')
	if 'extra' in l:
		print('&nbsp;' + l['extra'], end='')
	print('</li>', end='')

print('<div id="header"><nav><ul>', end='')
for l in navLinks:
	navLink(l)
print('</ul></nav>', end='')

# Header
print('<header><h1><a href="/"><img src="/img/logo/logo.svg" id="logo-img" alt="t^n"/> Etienne Perot</a>', end='')
if len(sys.argv) == 4:
	print(' &raquo; <a href="' + html.escape(sys.argv[2]) + '">' + html.escape(sys.argv[3]) + '</a>', end='')
else:
	for l in navLinks:
		if sys.argv[1] == l['name']:
			print(' &raquo; <a href="' + l['url'] + '">' + l['label'] + '</a>', end='')
print('</h1></header><div class="clearfix"></div></div>', end='')
