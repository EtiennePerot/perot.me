import re

_scriptRegex = re.compile('<script[^<>]*>(?!// @source)', re.IGNORECASE)
def process(f, content):
	return _scriptRegex.sub('\\g<0>// @source: git://perot.me/perot.me\n', content)
