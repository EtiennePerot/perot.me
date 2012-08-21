comment = """
<!--

Hi there!
The following is highly-minimized HTML, JavaScript, and CSS code, with some inlined content too.
It probably won't look very readable.
Don't worry though; prior to minimization, all of this is very readable, properly indented code.

The entire site is open source, should you want to check the original source files. You can view them on:
- Local git daemon:  git://perot.me/perot.me
- GitHub:            https://github.com/EtiennePerot/perot.me
- Bitbucket:         https://bitbucket.org/EtiennePerot/perot.me

-->
"""

def process(f, content):
	if comment not in content:
		content = content[:content.find('<html')] + comment + content[content.find('<html'):]
	return content
