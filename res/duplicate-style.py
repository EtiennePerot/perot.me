import re

# This may break when styles are device-specific
_duplicateStyleRegex = re.compile(r'</style>\s*<style[^<>]*>', re.IGNORECASE)
def process(f, content):
	return _duplicateStyleRegex.sub('\n', content)
