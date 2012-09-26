import time, datetime, hashlib, uuid, xml.etree.ElementTree
from email.utils import formatdate as rfc822format # I have no clue who thought it would be a good idea to put that there
rfc822 = lambda d : rfc822format(time.mktime(d.timetuple()))
from rfc3339 import rfc3339

class Node(xml.etree.ElementTree.Element):
	def __init__(self, tagname, content = None, *children, **attrs):
		xml.etree.ElementTree.Element.__init__(self, tagname, attrib=attrs)
		childrenNodes = list(children)
		if isinstance(content, Node):
			childrenNodes = [content] + childrenNodes
			content = None
		elif type(content) is type([]):
			childrenNodes = content
			content = None
		self.extend(childrenNodes)
		if content is not None:
			self.text = content

def uuidFromContent(content):
	return 'urn:uuid:' + str(uuid.UUID(bytes = hashlib.md5(content.encode('utf8')).digest(), version = 4))

def obfuscateEmail(email):
	return email.replace('.', ' (dot) ').replace('@', ' (at) ')

def formattedDate(d, rfc):
	if d is None:
		return None
	return rfc(d)

def getLastDate(entries):
	lastUpdate = None
	for e in entries:
		if lastUpdate is None or lastUpdate < e['updated']:
			lastUpdate = e['updated']
	return lastUpdate

def rss2Feed(title, mainUrl, entries, encoding='utf-8'):
	lastUpdate = getLastDate(entries)
	return ('<?xml version="1.0" encoding="' + encoding + '"?>' + xml.etree.ElementTree.tostring(Node('rss',
		Node('channel',
			[
				Node('title', title),
				Node('link', mainUrl),
				Node('link', href = mainUrl),
				Node('pubDate', formattedDate(lastUpdate, rfc822)),
			] + [
				Node('item',
					Node('title', e['title']),
					Node('link', e['url']),
					Node('guid', uuidFromContent(e['rawcontent'])),
					Node('pubDate', formattedDate(e['updated'], rfc822)),
					Node('author', obfuscateEmail(e['author'])),
					Node('description', e['content']),
				)
			for e in entries],
		),
		version = '2',
	), encoding='unicode')).encode(encoding)


def atomFeed(title, mainUrl, entries, encoding='utf-8'):
	lastUpdate = getLastDate(entries)
	return ('<?xml version="1.0" encoding="' + encoding + '"?>' + xml.etree.ElementTree.tostring(Node('feed',
		[
			Node('title', title),
			Node('link', rel = 'self', href = mainUrl),
			Node('link', href = mainUrl),
			Node('id', uuidFromContent(title)),
			Node('updated', formattedDate(lastUpdate, rfc3339)),
		] + [
			Node('entry',
				Node('title', e['title']),
				Node('link', href = e['url']),
				Node('id', uuidFromContent(e['rawcontent'])),
				Node('updated', formattedDate(e['updated'], rfc3339)),
				Node('author',
					Node('name', e['author-name']),
					Node('email', obfuscateEmail(e['author-email'])),
				),
				Node('content', e['content'], type = 'html'),
			)
		for e in entries],
		xmlns = 'http://www.w3.org/2005/Atom',
	), encoding='unicode')).encode(encoding)
