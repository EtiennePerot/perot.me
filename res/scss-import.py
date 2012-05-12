#!/usr/bin/env python2

import sys
files = sys.argv[1:]
if not len(files):
	print >> sys.stderr, 'Specify at least one file to parse.'

import os, re
inlineStyles = re.compile(r'(<style[^<>]*>)([\s\S]*)</style>', re.IGNORECASE)
scssImport = re.compile('\\s*@import\\s+([\'"])/*((?:\\\\.|(?!\\1).)+?)\\.scss\\1\\s*;\\s*', re.IGNORECASE)

def parseImport(d, m):
	cssPath, scssPath = os.path.join(d, m.group(2) + '.css'), os.path.join(d, m.group(2) + '.scss')
	while not os.path.isfile(cssPath) and not os.path.isfile(scssPath):
		if d == os.path.dirname(d): # Reached root directory, give up
			print >> sys.stderr, 'Neither the .scss or the .css file was found.'
			return '/* Neither the .scss or the .css file was found. */'
		d = os.path.dirname(d)
	if os.path.isfile(cssPath):
		handle = open(cssPath, 'rb')
		content = handle.read(-1).strip()
		handle.close()
		return content
	# .scss file exists, but not .css
	print >> sys.stderr, '.scss file found at', d, 'but corresponding .css file not found.'
	return '/* .scss file found but corresponding .css file not found */'

def parseStyle(d, m):
	return m.group(1) + scssImport.sub(lambda x : parseImport(d, x), m.group(2)) + '</style>'

for f in files:
	d = os.path.dirname(os.path.abspath(f))
	handle = open(f, 'rb')
	content = handle.read(-1)
	handle.close()
	newContent = inlineStyles.sub(lambda x : parseStyle(d, x), content)
	if content != newContent:
		handle2 = open(f, 'wb')
		handle2.write(newContent)
		handle2.close()
