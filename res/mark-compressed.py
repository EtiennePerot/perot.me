#!/usr/bin/env python2

import sys
files = sys.argv[1:]
if not len(files):
	print >> sys.stderr, 'Specify at least one file to parse.'

comment = """
<!--

Hi there!
The following is highly-minimized HTML, JavaScript, and CSS code, with some inlined content too.
It probably won't look very readable.
Don't worry though; prior to minimization, all of this is very readable and properly indented.

The entire site is open source, should you want to check the original source files. You can view them on:
- Local git daemon:  git://perot.me/perot.me
- GitHub:            https://github.com/EtiennePerot/perot.me
- Bitbucket:         https://bitbucket.org/EtiennePerot/perot.me

-->
"""

for f in files:
	handle = open(f, 'rb')
	content = handle.read(-1)
	handle.close()
	newContent = content[:content.find('<html')] + comment + content[content.find('<html'):]
	handle2 = open(f, 'wb')
	handle2.write(newContent)
	handle2.close()
