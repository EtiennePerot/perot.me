import os, re, hashlib, filefilter

resourceR = re.compile('([(\'"])(?:(?:https?:)?//perot\.me)?/((?:posts-)?img/[^?&)\'"]+)(?:\?[^\'")]*)?([\'")])', re.IGNORECASE)

def parseResource(f, m):
	url = m.group(2)
	resource = filefilter.findFile(f, url)
	if resource is None:
		resource = filefilter.findFile(f, url.replace('posts-img/', 'posts/'))
		if resource is None:
			return m.group(0) # Don't modify anything
	f = open(resource, 'rb')
	content = f.read(-1)
	f.close()
	extension = ''
	if '.' in url:
		extension = url[url.rfind('.'):]
		url = url[:url.rfind('.')]
	url = url + '-res-' + hashlib.md5(content).hexdigest()[:8] + extension
	return m.group(1) + '/' + url + m.group(3)

def process(f, content):
	if '<body' in content:
		return content[:content.find('<body')] +  resourceR.sub(lambda x : parseResource(f, x), content[content.find('<body'):])
	return content
