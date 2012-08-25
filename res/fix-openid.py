# Some OpenID clients don't support protocol-relative URLs
# Fix it by re-expanding those URLs.
def process(f, content):
	return content.replace('"//www.myopenid.com', '"https://www.myopenid.com').replace('"//EtiennePerot.myopenid.com', '"https://EtiennePerot.myopenid.com')
