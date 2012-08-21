import sys, os, re, requests, filefilter

scripts = re.compile(r'(<script[^<>]*>)([\s\S]*)</script>', re.IGNORECASE)
jsImport = re.compile('\\s*js_import\\s*\\(\\s*([\'"])/*((?:\\\\.|(?!\\1).)+?\\.js)\\1\\s*\\)', re.IGNORECASE)

def parseImport(f, m):
	if ':' in m.group(2):
		return requests.get(m.group(2)).text
	else:
		jsPath = filefilter.findFile(f, m.group(2))
		if jsPath is None:
			print('No .js file was found.', file=sys.stderr)
			return '/* No .js file was found. */'
		handle = open(jsPath, 'r', encoding='utf8')
		content = handle.read(-1).strip()
		handle.close()
		return content

def parseScript(f, m):
	return m.group(1) + jsImport.sub(lambda x : parseImport(f, x), m.group(2)) + '</script>'

def process(f, content):
	newContent = scripts.sub(lambda x : parseScript(f, x), content)
	while content != newContent:
		content = newContent
		newContent = scripts.sub(lambda x : parseScript(f, x), content)
	return newContent
