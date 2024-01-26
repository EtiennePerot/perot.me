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
blogDirFromPostsDir = '../../blog'
postsUrl = ''
postsAbsoluteUrl = 'https://perot.me'
postsResourceUrl = '/posts-img'
thumbFilename = 'thumb.png'
licenseDir = 'licenses'
templateFile = 'blogpost.template.html'
replyTemplateFile = 'comments/compose.template.php'
commentsTemplateFile = 'comments/comment.template.html'
excerptTemplateFile = 'blogpost-excerpt.template.html'
separatorTemplateFile = 'blogpost-excerpt-separator.template.html'
atomFile = '../posts.atom'
rss2File = '../posts.rss2'
breakMark = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
codeBreakMark = '~--~'
pygmentsStyle = 'manni'

_pygments_mod = __import__('pygments-bashsession-monkeypatch') # Patch pygment's bash session lexer
import os, sys, datetime, html, re, markdown
import xmldefs
from mannimod import ManniStyle_mod

sys.stdin = sys.stdin.detach()
sys.stdout = sys.stdout.detach()

scriptDir = os.path.dirname(sys.argv[0])
if scriptDir:
	os.chdir(scriptDir)

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

codeLanguageMatch = re.compile(r'^[ \t]+:{3,}([^\r\n]+)', re.MULTILINE)
def getCodeInfo(rawText, formattedText):
	codeLanguages = []
	for r in codeLanguageMatch.finditer(rawText):
		if r.group(1).lower() not in codeLanguages:
			codeLanguages.append(r.group(1).lower())
	return codeLanguages, len(codeLanguages) or '<code' in formattedText

def phpEscape(s):
	return '\'' + s.replace('\\', '\\\\').replace('\'', '\\\'') + '\''

class Comment:
	def __init__(self, post, text):
		self.post = post
		self.rawText = text
		self.index = None
		m = md()
		self.content = m.convert(self.rawText)
		self.content = self.content.replace('<a ', '<a rel="nofollow" ')
		self.date = datetime.datetime.strptime(m.Meta['date'][0], '%Y-%m-%d %H:%M:%S')
		self.author = None
		self.website = None
		if 'author' in m.Meta and m.Meta['author'][0].lower() != 'anonymous':
			self.author = m.Meta['author'][0]
			if 'website' in m.Meta: # URL is only valid if there is a valid author
				self.website = m.Meta['website'][0]
		self.codeLanguages, self.hasCodeTag = getCodeInfo(self.rawText, self.content)
	def __lt__(self, other):
		return self.date < other.date
	def __eq__(self, other):
		return self.post == other.post and self.date == other.date and self.content == other.content and self.author == other.author and self.website == other.website and self.rawText == other.rawText
	def setIndex(self, index):
		self.index = index
	def hasCode(self):
		return self.hasCodeTag
	def hasCodeLanguages(self):
		return len(self.codeLanguages)
	def getCodeLanguages(self):
		return self.codeLanguages
	def subst(self, template):
		content = template
		content = content.replace('%commentnumber%', str(self.index))
		if self.index % 2 == 0:
			content = content.replace('%commentevenodd%', 'even')
		else:
			content = content.replace('%commentevenodd%', 'odd')
		content = content.replace('%commentpubdate%', str(self.date)) # Formats as YYYY-MM-DD HH:MM:SS which is valid
		content = content.replace('%commentdate%', self.date.strftime('%Y-%m-%d %H:%M'))
		if self.author is None:
			content = content.replace('%commentauthor%', '<span class="comment-author comment-anonymous">Anonymous</span>')
		elif self.website is None:
			content = content.replace('%commentauthor%', '<span class="comment-author email-replace">' + html.escape(self.author) + '</span>')
		else:
			content = content.replace('%commentauthor%', '<a href="' + html.escape(self.website) + '" rel="nofollow" class="comment-author">' + html.escape(self.author) + '</a>')
		content = content.replace('%comment%', self.content)
		return content

class Post:
	authorMatch = re.compile(r'^\s*(\S(?:.*\S)?)\s*<([^<>]+)>$')
	linkMatch = re.compile(r'^\[([^]\r\n]+)\]:[ \t]*(\S+)(?:[ \t]+([^\r\n]+))?', re.MULTILINE)
	sourceSrcMatch = re.compile('(<source[^>]+src)="([^"]+)"', re.MULTILINE)
	videoSrcMatch = re.compile('(<video[^>]+src)="([^"]+)"', re.MULTILINE)
	videoPosterMatch = re.compile('(<video[^>]+poster)="([^"]+)"', re.MULTILINE)
	def __init__(self, text, baseUrl, m=None):
		self.baseUrl = baseUrl
		self.resourceUrl = postsResourceUrl + '/' + baseUrl
		self.rawText = text
		if m is None:
			m = md()
		text = text.replace(codeBreakMark, '<!-- -->')
		text = Post.linkMatch.sub(self._handleLink, text)
		text = Post.sourceSrcMatch.sub(self._handleHTMLAttribute, text)
		text = Post.videoSrcMatch.sub(self._handleHTMLAttribute, text)
		text = Post.videoPosterMatch.sub(self._handleHTMLAttribute, text)
		self.content = m.convert(text)
		self.title = m.Meta['title'][0]
		self.author = m.Meta['author'][0]
		# datetime.date doesn't have strptime
		self.date = datetime.date(*map(int, m.Meta['date'][0].split('-')))
		self.staging = 'staging' in m.Meta
		self.codeLanguages, self.hasCodeTag = getCodeInfo(text, self.content)
		self.url = postsUrl + '/' + baseUrl
		self.thumb = self.resourceUrl + '/' + thumbFilename
		self.thumbUrl = None
		if 'thumbnailurl' in m.Meta:
			self.thumbUrl = m.Meta['thumbnailurl'][0]
			if '/' not in self.thumbUrl and ':' not in self.thumbUrl:
				self.thumbUrl = (self.resourceUrl + '/' + self.thumbUrl).replace('//', '/')
		self.canonicalImage = self.thumb
		if 'canonicalimage' in m.Meta:
			self.canonicalImage = self.resourceUrl + '/' + m.Meta['canonicalimage'][0]
		self.license = None
		if 'license' in m.Meta:
			f = open(licenseDir + os.sep + m.Meta['license'][0].lower() + '.include.html', 'r', encoding='utf8')
			self.license = f.read(-1)
			f.close()
		self.comments = []
		commentsDir = filesystemPostsDir + os.sep + baseUrl + os.sep + 'comments'
		if os.path.isdir(commentsDir):
			for commentFile in os.listdir(commentsDir):
				if commentFile[-3:].lower() == '.md':
					f = open(commentsDir + os.sep + commentFile, 'r', encoding='utf8')
					commentText = f.read(-1)
					f.close()
					comment = Comment(self, commentText)
					self.comments.append(comment)
					self.hasCodeTag = self.hasCodeTag or comment.hasCode()
					self.codeLanguages.extend(comment.getCodeLanguages())
		self.comments.sort()
		for i, c in enumerate(self.comments):
			c.setIndex(i + 1)
	def _handleLink(self, match):
		url = match.group(2)
		if '/' not in url:
			url = (self.resourceUrl + '/' + url).replace('//', '/')
		title = match.group(3)
		if not title:
			title = '"' + match.group(1) + '"'
		return '[' + match.group(1) + ']: ' + url + ' ' + title
	def _handleHTMLAttribute(self, match):
		url = match.group(2)
		if '/' not in url:
			url = (self.resourceUrl + '/' + url).replace('//', '/')
		return match.group(1) + '="' + url + '"'
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
	def isStaging(self):
		return self.staging
	def getPubdate(self):
		return str(self.date) # Just happens to be valid YYYY-MM-DD format
	def getPrintableDate(self):
		return str(self.date)
	def getBaseUrl(self):
		return self.baseUrl
	def getUrl(self, full=True):
		if full:
			return postsAbsoluteUrl + self.url
		return self.url
	def getUrlMd(self):
		return self.url + '.md'
	def getCanonicalImage(self, full=True):
		if full:
			return postsAbsoluteUrl + self.canonicalImage
		return self.canonicalImage
	def getCommentFormUrl(self):
		return postsUrl + '/reply:' + self.baseUrl
	def getContent(self, withThumbnail=False, fullThumnail=False):
		if withThumbnail:
			if self.thumbUrl is not None:
				return '<p><a href="' + html.escape(self.getThumbUrl(full=fullThumnail)) + '"><img src="' + html.escape(self.getThumb(full=fullThumnail)) + '" title="' + html.escape(self.getTitle()) + '" alt="' + html.escape(self.getTitle()) + '"/></a></p>' + self.content
			return '<p><img src="' + html.escape(self.getThumb(full=fullThumnail)) + '" title="' + html.escape(self.getTitle()) + '" alt="' + html.escape(self.getTitle()) + '"/></p>' + self.content
		return self.content
	def getRawText(self):
		return self.rawText
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
	def getNumComments(self):
		return len(self.comments)
	def getComments(self):
		return self.comments

def substTemplate(template, p, commentsTemplate=None):
	content = template
	content = content.replace('%title%', html.escape(p.getTitle()))
	content = content.replace('%author%', html.escape(p.getAuthor()))
	content = content.replace('%date%', html.escape(p.getPrintableDate()))
	content = content.replace('%pubdate%', html.escape(p.getPubdate()))
	content = content.replace('%url%', html.escape(p.getUrl()))
	content = content.replace('%canonicalimage%', html.escape(p.getCanonicalImage()))
	content = content.replace('%mdurl%', html.escape(p.getUrlMd()))
	content = content.replace('%urlname%', html.escape(p.getBaseUrl()))
	content = content.replace('%thumbnail%', html.escape(p.getThumb()))
	content = content.replace('%blogdir%', html.escape(blogDirFromPostsDir))
	content = content.replace('%commentsdir%', html.escape(blogDirFromPostsDir + os.sep + 'comments'))
	content = content.replace('%numcomments%', html.escape(str(p.getNumComments())))
	if p.getNumComments() == 0:
		content = content.replace('%friendlycommentnum%', 'No comments')
	elif p.getNumComments() == 1:
		content = content.replace('%friendlycommentnum%', 'One comment')
	else:
		content = content.replace('%friendlycommentnum%', html.escape(str(p.getNumComments()) + ' comments'))
	if p.getThumbUrl() is not None:
		content = content.replace('%thumbnailurl%', html.escape(p.getThumbUrl()))
	else:
		content = content.replace('%thumbnailurl%', html.escape(p.getUrl()))
	content = content.replace('%commentformurl%', html.escape(p.getCommentFormUrl()))
	if '%commentliststart%' in content and '%commentlistend%' in content:
		if p.getNumComments():
			content = content.replace('%commentliststart%', '')
			content = content.replace('%commentlistend%', '')
		else:
			content = content[:content.find('%commentliststart%')] + content[content.find('%commentlistend%') + len('%commentlistend%'):]
	extraJS = []
	extraCSS = []
	if '%iscommentform%' in content:
		content = content.replace('%iscommentform%', '')
		extraJS.append('js_import("blog/comments/comment_form.js");')
		extraCSS.append('@import "blog/comments/comment_form.scss";')
	if p.hasCode():
		extraCSS.append('@import "inconsolata.css";')
		if p.hasCodeLanguages():
			from pygments.formatters import HtmlFormatter
			extraCSS.append(HtmlFormatter(style=ManniStyle_mod).get_style_defs('.codehilite'))
	if len(extraJS):
		content = content.replace('%extrajs%', '<script>' + '\n'.join(extraJS) + '</script>')
	else:
		content = content.replace('%extrajs%', '')
	if len(extraCSS):
		content = content.replace('%extracss%', '<style>' + '\n'.join(extraCSS) + '</style>')
	else:
		content = content.replace('%extracss%', '')
	if p.getLicense() is not None:
		content = content.replace('%license%', p.getLicense())
	content = content.replace('%content%', p.getContent())
	if commentsTemplate is not None and '%comments%' in content:
		# This must always be the last replacement, otherwise some smart commenters may post %stuff% and have it replaced.
		content = content.replace('%comments%', '\n'.join([c.subst(commentsTemplate) for c in p.getComments()]))
	return content

if __name__ == '__main__':
	if '--homepage' in sys.argv[1:]:
		templateSeparatorF = open(separatorTemplateFile, 'r', encoding='utf8')
		templateSeparator = templateSeparatorF.read(-1)
		templateSeparatorF.close()
		templateF = open(excerptTemplateFile, 'r', encoding='utf8')
		template = templateF.read(-1)
		templateF.close()
		posts = []
		for p in os.listdir(filesystemPostsDir):
			if not os.path.isdir(filesystemPostsDir + os.sep + p):
				continue
			f = open(filesystemPostsDir + os.sep + p + os.sep + p + '.md', 'r', encoding='utf8')
			content = f.read(-1)
			f.close()
			# Extract excerpt
			excerpt = ''
			pastBreakmark = False
			for l in content.split('\n'):
				if l and Post.linkMatch.search(l): # Link definition; keep this.
					excerpt +=  l + '\n'
				pastBreakmark = pastBreakmark or l == breakMark
				if not pastBreakmark:
					excerpt +=  l + '\n'
			post = Post(excerpt, p)
			if not post.isStaging():
				posts.append(post)
		posts.sort(key = lambda p : p.getDate(), reverse=True)
		if '--css' in sys.argv[1:]:
			hasCode = False
			hasCodeLanguages = False
			for p in posts:
				hasCode = hasCode or p.hasCode()
				hasCodeLanguages = hasCodeLanguages or hasCode or p.hasCodeLanguages()
			if hasCode:
				sys.stdout.write(b'@import "inconsolata.css";')
			if hasCodeLanguages:
				from pygments.formatters import HtmlFormatter
				sys.stdout.write(HtmlFormatter(style=ManniStyle_mod).get_style_defs('.codehilite').encode('utf8'))
		else:
			for p in posts:
				if p != posts[0]:
					sys.stdout.write(templateSeparator.encode('utf8'))
				sys.stdout.write(substTemplate(template, p).encode('utf8'))

	if '--make' in sys.argv[1:]:
		templateF = open(templateFile, 'r', encoding='utf8')
		template = templateF.read(-1)
		templateF.close()
		replyTemplateF = open(replyTemplateFile, 'r', encoding='utf8')
		replyTemplate = replyTemplateF.read(-1)
		replyTemplateF.close()
		commentsTemplateF = open(commentsTemplateFile, 'r', encoding='utf8')
		commentsTemplate = commentsTemplateF.read(-1)
		commentsTemplateF.close()
		postFilesInfo = {}
		feedEntries = []
		for p in os.listdir(filesystemPostsDir):
			if not os.path.isdir(filesystemPostsDir + os.sep + p):
				continue
			postInfo = {}
			postFilesInfo[p] = postInfo
			f = open(filesystemPostsDir + os.sep + p + os.sep + p + '.md', 'r', encoding='utf8')
			content = f.read(-1)
			f.close()
			content = content.replace(breakMark, '<a name="after-the-break"></a>') # Replace break mark by anchor
			post = Post(content, p)
			postInfo['title'] = post.getTitle()
			postInfo['url'] = post.getUrl()
			f = open(filesystemPostsDir + os.sep + p + os.sep + p + '.html', 'w', encoding='utf8')
			f.write(substTemplate(template, post, commentsTemplate))
			f.close()
			f = open(filesystemPostsDir + os.sep + p + os.sep + p + '_reply.php', 'w', encoding='utf8')
			f.write(substTemplate(replyTemplate, post, commentsTemplate))
			f.close()
			if not post.isStaging():
				feedEntries.append({
					'title': post.getTitle(),
					'author': post.getAuthor(),
					'author-name': post.getAuthorName(),
					'author-email': post.getAuthorEmail(),
					'content': post.getContent(withThumbnail=True, fullThumnail=True),
					'rawcontent': post.getRawText(),
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
		# Make comment system's list of posts
		commentsPostList = open('comments/article_list.gen.php', 'w', encoding='utf8')
		phpPostInfo = []
		for p in postFilesInfo:
			postInfo = []
			for k, v in postFilesInfo[p].items():
				postInfo.append(phpEscape(k) + ' => ' + phpEscape(v))
			phpPostInfo.append(phpEscape(p) + ' => array(' + ', '.join(postInfo) + ')')
		commentsPostList.write('<?php\n$all_articles = array(' + ', '.join(phpPostInfo) + ');\n?>')
		commentsPostList.close()
