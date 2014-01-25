import os, re, markdown, filefilter

rInclude = re.compile(r'<include([^<>]*)>((?:(?!</include>).)+)</include>', re.IGNORECASE)
rLinkMatch = re.compile(r'^\[([^]\r\n]+)\]:[ \t]*(\S+)(?:[ \t]+([^\r\n]+))?', re.MULTILINE)

def handleLink(match):
	url = match.group(2)
	if '/' not in url:
		url = (self.resourceUrl + '/' + url).replace('//', '/')
	title = match.group(3)
	if not title:
		title = '"' + match.group(1) + '"'
	return '[' + match.group(1) + ']: ' + url + ' ' + title

def processInclude(f, m):
	toInclude = filefilter.findFile(f, m.group(2).strip())
	if toInclude is None:
		return '<span class="error">Could not include file ' + m.group(2).strip() + '</span>'
	isMarkdown = 'markdown' in m.group(1).lower()
	hasPagebreak = 'replacepagebreak' in m.group(1).lower()
	handle = open(toInclude, 'r', encoding='utf8')
	content = handle.read(-1)
	handle.close()
	if isMarkdown:
		content = rLinkMatch.sub(handleLink, content)
		if hasPagebreak:
			content = content.replace('\\pagebreak', '')
		content = markdown.Markdown(
			extensions=['codehilite', 'meta', 'sane_lists'],
			extensions_configs={},
			output_format='html5',
			smart_emphasis=True
		).convert(content)
	return filefilter.process(f, content)

def process(f, content):
	return rInclude.sub(lambda m : processInclude(f, m), content)
