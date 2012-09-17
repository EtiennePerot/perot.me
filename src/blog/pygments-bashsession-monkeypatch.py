import re
from pygments.lexer import Lexer, do_insertions
from pygments.token import Generic, Comment
from pygments.lexers import shell

line_re  = re.compile('.*?\n')

class BashSessionLexer_mod(Lexer):
	name = 'Bash Session'
	aliases = ['console']
	filenames = ['*.sh-session']
	mimetypes = ['application/x-shell-session']
	def get_tokens_unprocessed(self, text):
		bashlexer = shell.BashLexer(**self.options)
		pos = 0
		curcode = ''
		insertions = []
		for match in line_re.finditer(text):
			line = match.group()
			m = re.match(r'^((?:[^@#$%\s]+@[^]#$%\s]+(?: ?:? ?\[?[^]#$%]+\]?)? *)?[$#%])(.*\n?)', line)
			if line.startswith('#'):
				yield match.start(), Comment, line
				insertions = []
				curcode = ''
			elif m:
				# To support output lexers (say diff output), the output
				# needs to be broken by prompts whenever the output lexer
				# changes.
				if not insertions:
					pos = match.start()
				insertions.append((len(curcode),
				                  [(0, Generic.Prompt, m.group(1))]))
				curcode += m.group(2)
			elif line.startswith('>'):
				insertions.append((len(curcode),
				                  [(0, Generic.Prompt, line[:1])]))
				curcode += line[1:]
			else:
				if insertions:
					toks = bashlexer.get_tokens_unprocessed(curcode)
					for i, t, v in do_insertions(insertions, toks):
						yield pos+i, t, v
				yield match.start(), Generic.Output, line
				insertions = []
				curcode = ''
		if insertions:
			for i, t, v in do_insertions(insertions,
			                             bashlexer.get_tokens_unprocessed(curcode)):
				yield pos+i, t, v

shell.BashSessionLexer = BashSessionLexer_mod
