#!/usr/bin/env python3

import os, sys

def findFile(contextFile, fileToFind):
	contextDir = os.path.abspath(contextFile)
	if not os.path.isdir(contextDir):
		contextDir = os.path.dirname(contextDir)
	while os.path.dirname(contextDir) != contextDir and not os.path.exists(contextDir + os.sep + fileToFind):
		contextDir = os.path.dirname(contextDir)
	if os.path.exists(contextDir + os.sep + fileToFind):
		return contextDir + os.sep + fileToFind
	return None

files = []
filters = []

def process(f, content):
	for fi in filters:
		content = fi(f, content)
	return content

if __name__ == '__main__':
	args = sys.argv[1:]
	for a in sys.argv[1:]:
		if a[0] == '+':
			f = __import__(a[1:])
			filters.append(f.process)
		else:
			files.append(a)
	if not len(files):
		print('Specify at least one file to parse.', file=sys.stderr)
		sys.exit(1)
	for f in files:
		if '.include' in f:
			continue
		handle = open(f, 'r', encoding='utf8')
		content = handle.read(-1)
		handle.close()
		originalContent = content
		newContent = process(f, content)
		while newContent != content:
			content = newContent
			newContent = process(f, content)
		if newContent != originalContent:
			handle2 = open(f, 'w', encoding='utf8')
			handle2.write(newContent)
			handle2.close()
