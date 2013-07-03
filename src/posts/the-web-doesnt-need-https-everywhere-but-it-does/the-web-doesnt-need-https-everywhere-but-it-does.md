Title:        The web doesn't need HTTPS everywhere, but it does need HTTPS Everywhere
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2013-06-30
License:      CC-BY-3.0
ThumbnailUrl: https://www.eff.org/https-everywhere

Mozilla has recently announced that Firefox will [block mixed "active" content by default in Firefox 23][Firefox blocking mixed content in Firefox 23], after [Chromium][Chromium: Block mixed content by default] and even [Internet Explorer][Internet Explorer 9 Mixed Content Warning Improved] implemented similar measures. "Mixed content" refers to content being served over [HTTP] (i.e. plaintext) from within an [HTTPS] (i.e. HTTP-over-[TLS]) webpage. "Active" content refers to content which can modify the [DOM] of a webpage, i.e. any resource which, once loaded, modifies the way the page it is included in is rendered. Blocking mixed content is an attempt to solve multiple problems:

* Web developers [implementing HTTPS incorrectly][How to deploy HTTPS correctly] or half-assedly.
* Avoiding [non-HTTPS-only cookies][Secure cookies], [referer headers][Referer header], [user-agent][User agent], and other sensitive data from leaking more than they need to.
* Encouraging HTTPS to be more widespread – [certainly a good thing][NSA PRISM program] despite HTTPS's shortcomings.

The purpose of this post is to explain why browsers are moving in this direction, why it is a good thing, and why HTTPS Everywhere goes further in that direction.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## The dangers of mixed content

It needs to be repeated that Firefox's default mixed content blocking only applies to mixed *active* content. Active content refers to any resource which can modify the page it is used on. What exactly does that mean?

### JavaScript

The elephant in the room. JavaScript can do whatever it pleases to a webpage: it can completely rewrite the page, it [can][Bitcoin JavaScript miner 1]&nbsp;[mine][Bitcoin JavaScript miner 2]&nbsp;[Bitcoins][Bitcoin JavaScript miner 3], it can request other resources (including other JavaScript files), make [arbitrary HTTP requests][XMLHttpRequest], it can [do OpenGL][WebGL], it can [record data from the camera and the microphone][WebRTC], etc. Definitely "active".

### Flash/Java/etc

Arbitrary plugins can do arbitrary things. Flash [can execute Javascript][Run JavaScript from Flash], and Java can execute [potentially unsandboxed][Java security] code. It goes without saying that this content is also "active".

### CSS

This one isn't so obvious, but it makes a lot of sense once you realize that being able to [MITM] the CSS file of `https://legit-website.tld/user/my-secret-username` allows you to do something like this:

	:::css
	body {
		background: url(http://legit-website.tld/404-this-webpage-probably-doesnt-exist-wqtrfey90u45h);
	}

This allows a network snooper to read the content of any non-HTTPS-only cookie that has been set by `legit-website.tld`. This cookie can then allow the snooper to take over your session and impersonate you.

Not scary enough? How about this: By only modifying the CSS file of `paypal.com`, we can turn PayPal's innocent "Send money" webpage...

[![PayPal "Send money" web page thumbnail][]][PayPal "Send money" web page]

... into this much-less-innocent one:

[![PayPal "Send money" web page (modified CSS) thumbnail][]][PayPal "Send money" web page (modified CSS)]

**You should definitely feel safer when CSS is being served over HTTPS**. CSS is *active* content.

### Fonts

Font files sound harmless on paper, on the same rank as images/audio/video. However, being able to MITM font files allows you to effectively change the text on a page (to the human viewing the rendered text, not to the computer) by modifying the way characters look. That way, the PayPal webpage could be made to look something like this:

[![PayPal "Send money" web page (modified font) thumbnail][]][PayPal "Send money" web page (modified font)]

... but only if the PayPal page in question uses custom fonts for these fields. Not as easy to pull off or as terribly effective as the CSS one, but still something that should be avoided if possible. Therefore, fonts are *active* content.

### Images

Images are passive content. Being able to MITM may be able to replace them with inappropriate content, or images containing misleading text, but the risk of abuse is not very high.

You may argue that replacing conveniently-located images on the page may yield a similar effect (for example, if there was an image right above the "Recipient" field, you could try to get the user to enter something in it by telling them to do so in the image). However, it is seldom possible. Fonts, on the other hand, allows the attacker to change any text on the webpage that uses this font. Additionally, a broken font isn't a very big deal (the text is simply displayed with the next font in the fallback list, or with the browser's default font); the webpage is still usable without all of its custom fonts. On the other hand, removing images from a webpage is much more likely to cause breakage or make the webpage unusuable.

### Audio/video

Similar to images, these may be able to give wrong information to the user, but cannot change the webpage itself.

### Frames

While frames can't modify the page they are embedded in, they can try to blend into it as much as possible, such that it is hard to tell that there is a frame at all on the webpage (from the perspective of someone who has never viewed the page before). Therefore, it is better to force them to be served HTTPS. Otherwise, an HTTP frame inside an HTTPS webpage may lead the user to think they are typing information in a secure form, when in fact they are typing it inside the insecure frame within the HTTPS webpage.

## What HTTPS provides

What do we get from HTTPS? First, it is important to state what may be obvious to some: HTTP headers may contain important data. This includes authentication cookies (the possession of which allows a network snooper to log in as someone else), referer information (the URL of the page the user came from; this may be private, or contain confidential URL parameters), and various identifying bits of information such as the [user-agent][User agent], accept-language header, etc. Some of these headers are always worth protecting (authentification cookies). Some of these are sometimes not that confidential (accept-language). Some of these headers may not exist or may not be necessary for a request to be successful (tracking cookies).

So what does HTTPS give us?

* **Confidentiality**: No one but the client and the server know what is being transmitted over the connection. This means information such as form data, account credentials, cookie information, referer header, etc. are all encrypted.
* **Integrity**: The client can be certain that the content was not modified while in transit.
* **Authentication**: The client can be certain that the content it received came from the server it thinks it came from.

Sounds good, right? Unfortunately, using HTTPS also means:

* **Higher latency**: The TLS handshake is not free. When initiating a secure connection, the client and the server need to exchange cryptographic information before they can communicate securely. This adds [a kit if overhead to every connection][SSL handshake latency]; 2 roundtrips for a naïve implementation. Fortunately, this can be minimized a lot (down to zero in the best case) using [TLS False Start], [Next Protocol Negotiation], [Snap Start], or even new network protocols like [QUIC].
* **Slower throughput**: Of course, encrypting and decrypting data when sending/receiving it takes more time than just sending/receiving raw data. However, it has been shown that this extra overhead is [not very significant][Overclocking SSL].
* **$$$$**: Free SSL certificates [exist][StartSSL], but are pretty rare to come by and usually come with significant limitations (good luck getting a free wildcard certificate). And if you want to go for an [Extended Validation (EV) Certificate][Extended Validation Certificate] (pretty much a requirement if you want to sell anything online), be ready to fork over major amounts of money. The flawed trust model of SSL is not the topic of this post, but plays an active role in hampering its widespread use.
* **Doesn't hide everything**: HTTPS doesn't hide your IP, or the fact that you are requesting data from a certain server. It also doesn't hide the domain name you're accessing, because most HTTPS client implementations now use [SNI][Server Name Indication], which reveals the domain name you are browsing in plaintext.
* **Hard to get right**: Setting up the web server is one thing, making sure the website is built for it is [another][How to deploy HTTPS correctly], and making sure things [keep scaling afterwards][Gmail blog: A need for speed: the path to a faster loading sequence] is yet another challenge. This is where much of the mixed content problems come from; developers on a deadline, or who do not fully understand the implications of this change, or who simply make mistakes.

## HTTPS is not required everywhere

Given HTTPS's limitations, it may seem sensible to not use it when it is not completely necessary. Indeed, certain scenarios only require a subset of HTTPS's security properties:

* Browsing websites where censorship is not an issue and is not likely to become one in the future: websites such as the [Portal Wiki], personal websites such as the one you're reading right now, corporate websites that just describe the company they're about, news sites or blogs covering non-sensitive subjects, etc. This type of website usually doesn't need any of HTTPS's security properties. As long as you don't log in, the only thing HTTPS would achieve is hiding the names of the pages you're reading from [whoever is listening on your connection][NSA]. You can easily [browse such websites anonymously][Tor Browser Bundle] if you feel a need to. Of course, this only holds **as long as you don't log in**.
* Publicly-verifiable information can benefit from confidentiality (so that network snoopers can't know what you are looking up), but not necessarily from integrity or authentication since the information you are getting can be verified in other ways. This includes Usenet/mailing list archives (subscribe to the mailing list if you want to verify that the web archives match the real content), public governmental and court records (go get the paper records if you want to verify them), etc. In these cases, integrity and authentication would only be a convenience, not a necessity.
* *Passive* content, such as images present on every webpage of a website (logo, header, footer, favicon, etc) doesn't need HTTPS. Having those served over HTTP is not a big deal, as long as the referer header doesn't leak (which is the case if the originating webpage is served over HTTPS). On the other hand, passive content present on a subset of a website's pages should be served over HTTPS in order to avoid leaking information about which page a user is viewing.
* *Active* mixed content that is present on every webpage of a website doesn't need confidentiality; it only needs integrity and authentication. Indeed, any network snooper knows you're browsing `cool-web-two-point-oh-website.tld`, and knows that all webpages on `cool-web-two-point-oh-website.tld` contain a `<script>` element which loads jQuery. Thus, the request for the JavaScript file containing jQuery doesn't need to be confidential. **It does, however, need to have authentication and integrity** so that it isn't possible to modify the JavaScript code in transit.

### DomainKeys for HTTP?

What can we do about this? Well, a reasonable idea for the last item would be to extend [DomainKeys] to web content. DomainKeys is [a system for email authentication (DKIM)][DomainKeys Identified Mail]; it ensures that an email message was sent from a mail server that should have sent it. It works by adding a [public key][Public-key cryptography] in a [DNS record]. When the DKIM-enabled mail server sends a message, it [cryptographically signs][Digital signature] some of the outgoing email's headers and the email's body using the private key corresponding to the key published in the DNS record. When a mail server receives this signed email, it grabs the public key of the sending domain from DNS, and verifies the signature against it. If the signature is valid, then the email is guaranteed to have come from the originating domain. (At least, as long as DNS itself can be trusted; yet another topic for a future post, perhaps?)

We could easily extend this concept to HTTP. A web server could cryptographically sign the response it is serving, and put this signature in an HTTP header of the response. The HTTP exchange would look like this:

Request:

	:::http
	GET /js/jquery.js HTTP/1.1
	Host: legit-website.tld

The browser may initiate a DNS request for the public key of `legit-website.tld` in parallel with this request. This only needs to be done once per domain. The public key could also come from the SSL certificate of the originating webpage, in which case there is no need for any extra request.

Response:

	:::http
	HTTP/1.1 200 OK
	Content-Type: application/javascript
	Content-Length: 1337
	X-DomainKeys-Signature: v=1; a=rsa-sha512; signature=(signature goes here)
	
	/*! jQuery v1.10.1 | (c) 2005, 2013 jQuery Foundation, Inc. | jquery.org/license
	//@ sourceMappingURL=jquery-1.10.1.min.map
	*/
	(function(e,t) {
	... jQuery code continues ...

The browser can then check the signature (contained in the `X-DomainKeys-Signature` header) against the public key obtained from DNS. If the signature is valid, then the JavaScript code is considered valid and is interpreted. If not, then the browser considers the request to have failed, and the JavaScript code is discarded. The signature should cover the body, but also the URL, the content-type, and perhaps also contain a date range for validity, in order to prevent signatures to be used for other resources than the ones they were meant for, and to invalidate them after a period of time.

This scheme could work for any HTTP content, mixed or not. It effectively moves the integrity and authentication properties into the HTTP protocol itself, rather than having it be done at the TLS level. It has no latency penalty and very little computational overhead, because the signature can be computed ahead of time and stored on disk (or in memory), only needing recomputation when the resource's body changes or when the signature expires.

Unfortunately, deploying this scheme would require modifying existing websites, existing web servers, existing HTTP libraries, and existing browsers. Is it really worth it, when we already have a solution which provides the security properties we are after?

## The case for HTTPS Everywhere

Any scheme which tries to segment a website's resources according to their desired security properties is bound to fail. Developers already have a hard time [deploying HTTPS correctly][Troy Hunt: Your login form posts to HTTPS, but you blew it when you loaded it over HTTP], if [at][Reddit: Y u no SSL?]&nbsp;[all][Ubuntu shopping lens: Send traffic over HTTPS]; it is not a good idea to rely on individual websites to properly deploy this scheme everywhere, in such a way that all HTTP resources are signed when needed.

It doesn't make sense from the browser's perspective either: When stumbling upon an HTTP-served resource inside an HTTPS webpage, the browser cannot guess whether or not this was intentional on part of the developers (such that loading this resource over HTTP will not cause any privacy or security issues), or if it was just an oversight. As the second possibility is overwhelmingly more likely than the first, it is simply not advisable for browsers to choose to load mixed content by default. This could be worked around by adding an indication for the browser on the secure webpage, such as:

	::::html
	<script type="text/javascript" src="http-yes-really-i-know-this-is-mixed://legit-website.tld/js/jquery.js"></script>

... but that is clearly a hack. It still requires developers to carefully develop their applications and consider where information could leak, as opposed to simply [boiling the sea and encrypting all the things][Coding Horror: Should All Web Traffic Be Encrypted?]. It may not be as efficient as it can be, but it's simple and does the job. This type of solution usually wins out, through the [Worse Is Better principle], at least until they are not good enough anymore. HTTPS itself probably suffered from this as well; it wasn't until recently that its popularity has risen significantly. The web needed wake-up calls such as [Firesheep], [sslstrip], [Narus devices][Room 641A], and [other][ECHELON]&nbsp;[large-scale][Trailblazer]&nbsp;[traffic][Stellar Wind]&nbsp;[snooping][PRISM]&nbsp;[operations][Boundless Informant] which prompted large targets such as [Gmail][Gmail turns on SSL by default], [Twitter][Twitter turns on SSL by default] or [Facebook][Facebook turns on SSL by default] to turn on HTTPS by default for all users.

Ultimately, HTTPS provides the security properties necessary for everything at a reasonable cost. It's not the ideal solution, but it is *a* solution, and it is the best we have that is widely available right now.

Enter [HTTPS Everywhere] by the [Electronic Frontier Foundation]. It is a browser extension which automatically switches HTTP requests to HTTPS for sites which support it. Effectively, it acts much as the way your browser would on sites which have a permanent [HSTS header]. As a result, it addresses a lot of the practical shortcomings of HTTPS:

* Sites which support HTTPS but don't have an HSTS header now effectively have one. You now browse websites over HTTPS whenever it's possible to do so.
* HTTP Sites which contain resources from domains that support HTTPS are downloaded over HTTPS, which avoids leaking your referer to these domains and avoids these resources being MITM. This is a bigger deal than it appears; for example, a lot of websites include most of their JavaScript libraries from [Google's CDN][Google Hosted Libraries], rather than hosting a local copy of their own. As Google's CDN supports HTTPS, a lot of websites now have part of their JavaScript served securely.
* HTTPS websites that erroneously refer to HTTP resources (and would thus cause a "mixed content" error) now work correctly.
* When visiting a site that doesn't use HSTS headers (which is the vast majority of websites), you are not vulnerable to [SSL stripping attacks][sslstrip] anymore.
* When visiting a site that does use HSTS headers, you are not vulnerable to SSL stripping attacks when you visit it for the first time, or when its HSTS header expires.
* Typing a domain name in your browser's address bar goes to the HTTPS version of that website, rather than defaulting to HTTP.

The first half of this list is about fixing common problems resulting from *poor HTTPS implementations on websites*. The second half is about making the browser behaving in a more secure-by-default way.

## Conclusion

Here's the takeaway in bullet-point form:

* HTTPS is far from perfect, but it's the best available solution there is right now which covers most use cases.
* Not everything needs HTTPS, but the (much) bigger problem is HTTPS not being used where it should be.
* Browsers are moving in the right direction, but slowly.
* We can't rely on all websites to implement HTTPS properly on their end.
* Right now, a good way to partially address the problem is to use [HTTPS Everywhere].

[Firefox blocking mixed content in Firefox 23]: https://blog.mozilla.org/tanvi/2013/04/10/mixed-content-blocking-enabled-in-firefox-23/
[Chromium: Block mixed content by default]: https://code.google.com/p/chromium/issues/detail?id=81637
[Internet Explorer 9 Mixed Content Warning Improved]: https://blog.httpwatch.com/2011/05/04/ie-9-whats-changed/
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[HTTPS]: https://en.wikipedia.org/wiki/HTTP_Secure
[TLS]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[DOM]: https://en.wikipedia.org/wiki/Document_Object_Model
[How to deploy HTTPS correctly]: https://www.eff.org/https-everywhere/deploying-https
[Secure cookies]: https://en.wikipedia.org/wiki/HTTP_cookie#Secure_and_HttpOnly
[Referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[User agent]: https://en.wikipedia.org/wiki/User_agent
[NSA PRISM program]: https://en.wikipedia.org/wiki/PRISM_%28surveillance_program%29
[Bitcoin JavaScript miner 1]: http://www.bitcoinplus.com/miner/embeddable
[Bitcoin JavaScript miner 2]: https://github.com/progranism/Bitcoin-JavaScript-Miner
[Bitcoin JavaScript miner 3]: http://bitcoin.biniok.net/gl.html
[XMLHttpRequest]: https://en.wikipedia.org/wiki/XMLHttpRequest
[WebGL]: https://en.wikipedia.org/wiki/WebGL
[WebRTC]: https://en.wikipedia.org/wiki/WebRTC
[Run JavaScript from Flash]: http://stackoverflow.com/questions/9495146/javascript-calling-javascript-function-from-flash-swfobject
[Java security]: https://en.wikipedia.org/wiki/Java_security
[MITM]: https://en.wikipedia.org/wiki/Man-in-the-middle_attack
[PayPal "Send money" web page]: paypal-sendmoney.png
[PayPal "Send money" web page thumbnail]: paypal-sendmoney-thumb.png
[PayPal "Send money" web page (modified CSS)]: paypal-sendmoney-modcss.png
[PayPal "Send money" web page (modified CSS) thumbnail]: paypal-sendmoney-modcss-thumb.png
[PayPal "Send money" web page (modified font)]: paypal-sendmoney-modfont.png
[PayPal "Send money" web page (modified font) thumbnail]: paypal-sendmoney-modfont-thumb.png
[SSL handshake latency]: http://www.semicomplete.com/blog/geekery/ssl-latency.html
[TLS False Start]: https://tools.ietf.org/html/draft-bmoeller-tls-falsestart-00
[Next Protocol Negotiation]: https://tools.ietf.org/html/draft-agl-tls-nextprotoneg-00
[Snap Start]: https://tools.ietf.org/html/draft-agl-tls-snapstart-00
[QUIC]: http://blog.chromium.org/2013/06/experimenting-with-quic.html
[Overclocking SSL]: https://www.imperialviolet.org/2010/06/25/overclocking-ssl.html
[StartSSL]: https://www.startssl.com/
[Extended Validation Certificate]: https://en.wikipedia.org/wiki/Extended_Validation_Certificate
[Server Name Indication]: https://en.wikipedia.org/wiki/Server_Name_Indication
[Gmail blog: A need for speed: the path to a faster loading sequence]: https://gmailblog.blogspot.com/2008/05/need-for-speed-path-to-faster-loading.html
[Portal Wiki]: http://theportalwiki.com/
[NSA]: https://en.wikipedia.org/wiki/National_Security_Agency
[Tor Browser Bundle]: https://www.torproject.org/download/download-easy.html.en
[jQuery]: http://jquery.com/
[DomainKeys]: https://en.wikipedia.org/wiki/DomainKeys
[DomainKeys Identified Mail]: https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail
[Public-key cryptography]: https://en.wikipedia.org/wiki/Public_key_cryptography
[DNS record]: https://en.wikipedia.org/wiki/Domain_Name_System#DNS_resource_records
[Digital signature]: https://en.wikipedia.org/wiki/Digital_signature
[Troy Hunt: Your login form posts to HTTPS, but you blew it when you loaded it over HTTP]: http://www.troyhunt.com/2013/05/your-login-form-posts-to-https-but-you.html
[Reddit: Y u no SSL?]: http://www.reddit.com/r/AskReddit/comments/pz5kx/reddit_y_u_no_ssl/
[Ubuntu shopping lens: Send traffic over HTTPS]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1055649
[Coding Horror: Should All Web Traffic Be Encrypted?]: http://www.codinghorror.com/blog/2012/02/should-all-web-traffic-be-encrypted.html
[Worse Is Better principle]: https://en.wikipedia.org/wiki/Worse_is_better
[Firesheep]: https://en.wikipedia.org/wiki/Firesheep
[sslstrip]: https://github.com/moxie0/sslstrip
[Room 641A]: https://en.wikipedia.org/wiki/Room_641A
[ECHELON]: https://en.wikipedia.org/wiki/ECHELON
[Trailblazer]: https://en.wikipedia.org/wiki/Trailblazer_Project
[Stellar Wind]: https://en.wikipedia.org/wiki/Stellar_Wind_%28code_name%29
[PRISM]: https://en.wikipedia.org/wiki/PRISM_%28surveillance_program%29
[Boundless Informant]: https://en.wikipedia.org/wiki/Boundless_Informant
[Gmail turns on SSL by default]: https://gmailblog.blogspot.com/2010/01/default-https-access-for-gmail.html
[Twitter turns on SSL by default]: https://blog.twitter.com/2012/securing-your-twitter-experience-https
[Facebook turns on SSL by default]: https://developers.facebook.com/blog/post/2012/11/14/platform-updates--operation-developer-love/
[HTTPS Everywhere]: https://www.eff.org/https-everywhere
[Electronic Frontier Foundation]: https://www.eff.org/
[Google Hosted Libraries]: https://developers.google.com/speed/libraries/
[HSTS header]: https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security
