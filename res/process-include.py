import os, re, markdown, filefilter

rInclude = re.compile(r'<include([^<>]*)>((?:(?!</include>).)+)</include>', re.IGNORECASE)

def processInclude(f, m):
	toInclude = filefilter.findFile(f, m.group(2).strip())
	if toInclude is None:
		return '<span class="error">Could not include file ' + m.group(2).strip() + '</span>'
	isMarkdown = 'markdown' in m.group(1).lower()
	handle = open(toInclude, 'r', encoding='utf8')
	content = handle.read(-1)
	handle.close()
	if isMarkdown:
		content = markdown.Markdown(
			extensions=['codehilite', 'meta', 'sane_lists'],
			extensions_configs={},
			output_format='html5',
			smart_emphasis=True
		).convert(content)
	return filefilter.process(f, content)

def process(f, content):
	return rInclude.sub(lambda m : processInclude(f, m), content)
