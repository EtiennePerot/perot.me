import os, re, subprocess, html, filefilter

rExec = re.compile(r'<exec>((?:(?!</exec>).)+)</exec>', re.IGNORECASE)

def processExec(f, m):
	command = m.group(1).strip()
	try:
		output = subprocess.check_output(command, shell=True, cwd=os.path.dirname(f), stderr=open(os.devnull, 'wb'))
		return filefilter.process(f, output.decode('utf8').strip())
	except subprocess.CalledProcessError as e:
		try:
			output = subprocess.check_output('./' + command, shell=True, cwd=os.path.dirname(f), stderr=open(os.devnull, 'wb'))
			return filefilter.process(f, output.decode('utf8').strip())
		except:
			return '<span class="exec-error">Error while executing command: <code>' + html.escape(command) + '</code> (return code: <strong>' + str(e.returncode) + '</strong>).</span>'

def process(f, content):
	return rExec.sub(lambda m : processExec(f, m), content)
