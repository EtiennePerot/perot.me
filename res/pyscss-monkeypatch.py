#!/usr/bin/env python2

import os, sys, logging, inspect, base64

logging.basicConfig()

newArgv = []
staticUrl = None
assetsUrl = None
i = 0
while i < len(sys.argv):
	v = sys.argv[i]
	if v == '--static-url':
		staticUrl = sys.argv[i + 1]
		i += 1
	elif v == '--assets-url':
		assetsUrl = sys.argv[i + 1]
		if len(assetsUrl) and assetsUrl[-1] != '/':
			assetsUrl += '/'
		i += 1
	else:
		newArgv.append(v)
	i += 1

sys.argv = newArgv

originalJoin = os.path.join
def join(d1, *ds):
	newds = []
	for d in ds:
		if len(d) and d[0] == '/':
			d = d[1:]
		newds.append(d)
	return originalJoin(d1, *newds)
os.path.join = join

pyscss_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], 'pyscss')))
if pyscss_subfolder not in sys.path:
	sys.path.insert(0, pyscss_subfolder)

import scss as _scss_mod
_scss_mod.STATIC_URL = staticUrl or _scss_mod.STATIC_URL
_scss_mod.ASSETS_URL = assetsUrl or _scss_mod.ASSETS_URL

__scss_original___image_url = _scss_mod.__image_url
def _image_url_wrapper_gifcopy(path, only_path=False, cache_buster=True, dst_color=None, src_color=None, inline=False, mime_type=None):
	filepath = _scss_mod.StringValue(path).value
	if inline and not callable(_scss_mod.STATIC_ROOT) and filepath[-4:].lower() == '.gif':
		gifpath = os.path.join(_scss_mod.STATIC_ROOT, filepath)
		if os.path.exists(gifpath):
			gif_handle = open(gifpath, 'rb')
			gif_content = gif_handle.read(-1)
			gif_handle.close()
			url = 'data:image/gif;base64,' + base64.b64encode(gif_content)
			if not only_path:
				url = 'url("%s")' % _scss_mod.escape(url)
			return _scss_mod.StringValue(url)
	return __scss_original___image_url(
		path = path,
		only_path = only_path,
		cache_buster = cache_buster,
		dst_color = dst_color,
		src_color = src_color,
		inline = inline,
		mime_type = mime_type
	)

_scss_mod.__image_url = _image_url_wrapper_gifcopy

from scss import *
if __name__ == '__main__':
	main()
