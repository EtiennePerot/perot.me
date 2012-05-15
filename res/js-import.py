#!/usr/bin/env python2

import sys
files = sys.argv[1:]
if not len(files):
	print >> sys.stderr, 'Specify at least one file to parse.'

import os, re, urllib2
scripts = re.compile(r'(<script[^<>]*>)([\s\S]*)</script>', re.IGNORECASE)
jsImport = re.compile('\\s*import\\s*\\(\\s*([\'"])/*((?:\\\\.|(?!\\1).)+?\\.js)\\1\\s*\\)', re.IGNORECASE)

def parseImport(d, m):
	if ':' in m.group(2):
		return urllib2.urlopen(m.group(2)).read(-1)
	else:
		jsPath = os.path.join(d, m.group(2))
		while not os.path.isfile(jsPath):
			if d == os.path.dirname(d): # Reached root directory, give up
				print >> sys.stderr, 'No .js file was found.'
				return '/* No .js file was found. */'
			d = os.path.dirname(d)
		handle = open(jsPath, 'rb')
		content = handle.read(-1).strip()
		handle.close()
		return content

def parseScript(d, m):
	return m.group(1) + jsImport.sub(lambda x : parseImport(d, x), m.group(2)) + '</script>'

for f in files:
	d = os.path.dirname(os.path.abspath(f))
	handle = open(f, 'rb')
	content = handle.read(-1)
	handle.close()
	newContent = scripts.sub(lambda x : parseScript(d, x), content)
	if content == newContent:
		continue
	while content != newContent:
		content = newContent
		newContent = scripts.sub(lambda x : parseScript(d, x), content)
	handle2 = open(f, 'wb')
	handle2.write(newContent)
	handle2.close()
