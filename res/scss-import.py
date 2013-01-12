import sys, os, re, filefilter
inlineStyles = re.compile(r'(<style[^<>]*>)(.*)</style>', re.IGNORECASE | re.DOTALL)
scssImport = re.compile(r'@import\s+([\'"])/*((?:\\.|(?!\1).)+?)\.s?css\1;', re.IGNORECASE)

def parseImport(f, m):
	cssPath = filefilter.findFile(f, m.group(2) + '.css')
	scssPath = filefilter.findFile(f, m.group(2) + '.scss')
	if cssPath is None:
		if scssPath is None:
			return '/* Neither the .scss or the .css file was found. */'
		return '/* .scss file found but corresponding .css file not found */'
	handle = open(cssPath, 'r', encoding='utf8')
	content = handle.read(-1).strip()
	handle.close()
	return content
	

def parseStyle(f, m):
	return m.group(1) + scssImport.sub(lambda x : parseImport(f, x), m.group(2)) + '</style>'

def process(f, content):
	return inlineStyles.sub(lambda x : parseStyle(f, x), content)
