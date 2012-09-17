#!/usr/bin/env python2

import os, sys, logging, inspect

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
from scss import *
if __name__ == '__main__':
	main()
