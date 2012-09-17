#!/usr/bin/env python3

blogInfo = {
	'title': 'Etienne Perot\'s blog',
	'link': 'https://perot.me/',
	'description': 'Cool technology uses, personal project updates, and miscellaneous interesting things.',
	'author_name': 'Etienne Perot',
	'author_email': 'etienne at perot dot me',
	'author_link': 'https://perot.me/'
}
filesystemPostsDir = '../posts'
postsUrl = ''
postsAbsoluteUrl = 'https://perot.me'
postsResourceUrl = '/posts-img'
thumbFilename = 'thumb.png'
licenseDir = 'licenses'
templateFile = 'blogpost.template.html'
excerptTemplateFile = 'blogpost-excerpt.template.html'
atomFile = '../posts.atom'
rss2File = '../posts.rss2'
breakMark = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
codeBreakMark = '~--~'
pygmentsStyle = 'manni'

_pygments_mod = __import__('pygments-bashsession-monkeypatch') # Patch pygment's bash session lexer
import os, sys, datetime, html, re, markdown
import xmldefs
from mannimod import ManniStyle_mod

os.chdir(os.path.dirname(sys.argv[0]))

def md(extensions=[], extension_configs={}, **kwargs):
	keywordargs = {
		'extensions': ['codehilite', 'meta', 'sane_lists'] + extensions,
		'extensions_configs': {
			'codehilite': [
				('style', pygmentsStyle)
			]
		},
		'output_format': 'html5',
		'smart_emphasis': True
	}
	keywordargs['extensions_configs'].update(extension_configs)
	keywordargs.update(kwargs)
	m = markdown.Markdown(**keywordargs)
	return m

class Post:
	authorMatch = re.compile(r'^\s*(\S(?:.*\S)?)\s*<([^<>]+)>$')
	codeLanguageMatch = re.compile(r'^[ \t]+:{3,}([^\r\n]+)', re.MULTILINE)
	def __init__(self, text, baseUrl, m=None):
		if m is None:
			m = md()
		text = text.replace(codeBreakMark, '<!-- -->')
		self.content = m.convert(text)
		self.title = m.Meta['title'][0]
		self.author = m.Meta['author'][0]
		self.date = datetime.date(*map(int, m.Meta['date'][0].split('-')))
		self.codeLanguages = []
		for r in Post.codeLanguageMatch.finditer(text):
			if r.group(1).lower() not in self.codeLanguages:
				self.codeLanguages.append(r.group(1).lower())
		self.url = postsUrl + '/' + baseUrl
		self.resourceUrl = postsResourceUrl + '/' + baseUrl
		self.thumb = self.resourceUrl + '/' + thumbFilename
		self.thumbUrl = None
		if 'thumbnailurl' in m.Meta:
			self.thumbUrl = m.Meta['thumbnailurl'][0]
			if '/' not in self.thumbUrl and ':' not in self.thumbUrl:
				self.thumbUrl = self.url + '/' + self.thumbUrl
		self.hasCodeTag = self.hasCodeLanguages() or '<code' in self.content
		self.license = None
		if 'license' in m.Meta:
			f = open(licenseDir + os.sep + m.Meta['license'][0].lower() + '.include.html', 'r', encoding='utf8')
			self.license = f.read(-1)
			f.close()
	def getTitle(self):
		return self.title
	def getAuthor(self):
		return self.author
	def getAuthorName(self):
		res = Post.authorMatch.search(self.author)
		if res:
			return res.group(1)
	def getAuthorEmail(self):
		res = Post.authorMatch.search(self.author)
		if res:
			return res.group(2)
	def getDate(self):
		return self.date
	def getPrintableDate(self):
		return str(self.date)
	def getUrl(self, full=True):
		if full:
			return postsAbsoluteUrl + self.url
		return self.url
	def getUrlMd(self):
		return self.url + '.md'
	def getContent(self, withThumbnail=False, fullThumnail=False):
		if withThumbnail:
			if self.thumbUrl is not None:
				return '<p><a href="' + html.escape(self.getThumbUrl(full=fullThumnail)) + '"><img src="' + html.escape(self.getThumb(full=fullThumnail)) + '" title="' + html.escape(self.getTitle()) + '" alt="' + html.escape(self.getTitle()) + '"/></a></p>' + self.content
			return '<p><img src="' + html.escape(self.getThumb(full=fullThumnail)) + '" title="' + html.escape(self.getTitle()) + '" alt="' + html.escape(self.getTitle()) + '"/></p>' + self.content
		return self.content
	def getThumb(self, full=False):
		if full:
			return postsAbsoluteUrl + self.thumb
		return self.thumb
	def getThumbUrl(self, full=False):
		if full:
			return postsAbsoluteUrl + self.thumbUrl
		return self.thumbUrl
	def hasCode(self):
		return self.hasCodeTag
	def getLicense(self):
		return self.license
	def hasCodeLanguages(self):
		return len(self.codeLanguages)
	def getCodeLanguages(self):
		return self.codeLanguages

def substTemplate(template, p):
	content = template
	content = content.replace('%title%', html.escape(p.getTitle()))
	content = content.replace('%author%', html.escape(p.getAuthor()))
	content = content.replace('%date%', html.escape(p.getPrintableDate()))
	content = content.replace('%url%', html.escape(p.getUrl()))
	content = content.replace('%mdurl%', html.escape(p.getUrlMd()))
	content = content.replace('%thumbnail%', html.escape(p.getThumb()))
	if p.getThumbUrl() is not None:
		content = content.replace('%thumbnailurl%', html.escape(p.getThumbUrl()))
	else:
		content = content.replace('%thumbnailurl%', html.escape(p.getUrl()))
	if p.hasCode():
		if p.hasCodeLanguages():
			from pygments.formatters import HtmlFormatter
			highlightCss = HtmlFormatter(style=ManniStyle_mod).get_style_defs('.codehilite')
			content = content.replace('%extracss%', '<style>@import "inconsolata.css";\n' + highlightCss + '\n</style>')
		else:
			content = content.replace('%extracss%', '<style>@import "inconsolata.css";</style>')
	else:
		content = content.replace('%extracss%', '')
	if p.getLicense() is not None:
		content = content.replace('%license%', p.getLicense())
	content = content.replace('%content%', p.getContent())
	return content

if '--homepage' in sys.argv[1:]:
	templateF = open(excerptTemplateFile, 'r', encoding='utf8')
	template = templateF.read(-1)
	templateF.close()
	posts = []
	for p in os.listdir(filesystemPostsDir):
		if p[-3:].lower() != '.md':
			continue
		f = open(filesystemPostsDir + os.sep + p, 'r', encoding='utf8')
		content = f.read(-1)
		f.close()
		# Extract excerpt
		excerpt = ''
		pastBreakmark = False
		for l in content.split('\n'):
			if l and l[0] == '[': # Link definition; keep this.
				excerpt +=  l + '\n'
			pastBreakmark = pastBreakmark or l == breakMark
			if not pastBreakmark:
				excerpt +=  l + '\n'
		posts.append(Post(excerpt, p[:-3]))
	posts.sort(key = lambda p : p.getDate(), reverse=True)
	if '--css' in sys.argv[1:]:
		hasCode = False
		hasCodeLanguages = False
		for p in posts:
			hasCode = hasCode or p.hasCode()
			hasCodeLanguages = hasCodeLanguages or hasCode or p.hasCodeLanguages()
		if hasCode:
			print('@import "inconsolata.css";')
		if hasCodeLanguages:
			from pygments.formatters import HtmlFormatter
			print(HtmlFormatter(style=ManniStyle_mod).get_style_defs('.codehilite'))
	else:
		for p in posts:
			print(substTemplate(template, p))

if '--make' in sys.argv[1:]:
	templateF = open(templateFile, 'r', encoding='utf8')
	template = templateF.read(-1)
	templateF.close()
	feedEntries = []
	for p in os.listdir(filesystemPostsDir):
		if p[-3:].lower() != '.md':
			continue
		f = open(filesystemPostsDir + os.sep + p, 'r', encoding='utf8')
		content = f.read(-1)
		f.close()
		content = content.replace('\n' + breakMark + '\n', '') # Strip break mark
		post = Post(content, p[:-3])
		f2 = open(filesystemPostsDir + os.sep + p[:-3] + '.html', 'w', encoding='utf8')
		f2.write(substTemplate(template, post))
		f2.close()
		feedEntries.append({
			'title': post.getTitle(),
			'author': post.getAuthor(),
			'author-name': post.getAuthorName(),
			'author-email': post.getAuthorEmail(),
			'content': post.getContent(withThumbnail=True, fullThumnail=True),
			'url': post.getUrl(full=True),
			'updated': post.getDate(),
			'post': post
		})
	feedEntries.sort(key = lambda p : p['post'].getDate(), reverse=True)
	# Trim to latest 50 entries
	feedEntries = feedEntries[:min(len(feedEntries), 50)]
	atomFeed = open(atomFile, 'wb')
	atomFeed.write(xmldefs.atomFeed(
		title = blogInfo['title'],
		mainUrl = blogInfo['link'],
		entries = feedEntries
	))
	atomFeed.close()
	rss2Feed = open(rss2File, 'wb')
	rss2Feed.write(xmldefs.rss2Feed(
		title = blogInfo['title'],
		mainUrl = blogInfo['link'],
		entries = feedEntries
	))
	rss2Feed.close()