Title:        Ubuntu privacy blunder over Amazon ads continues
Author:       Etienne Perot <etienne (at) perot (dot) me>
Date:         2012-09-25
License:      CC-BY-3.0
ThumbnailUrl: dataleak.png

First, some context: There's been quite a few [complaints][The Register: Fans revolt over Amazon 'adware' in Ubuntu desktop search results] and [concerns][Ars Technica: Ubuntu bakes Amazon search results into OS to raise cash] about [Ubuntu]'s [attempt to include advertisements in their operating system][Online Shopping Feature Arrives in Ubuntu 12.10], in the form of [Amazon-affiliate-tracked][Amazon affiliate program] results showing up in [Unity]'s Dash interface by default. There has also been [some attempts][Lots of Hype Over Shopping Lens in Ubuntu 12.10] to do some [damage control][More Information About Online Dash Search Privacy] over this PR disaster, including [one by Mark Shuttleworth himself][Amazon search results in the Dash], Ubuntu's Self-Appointed Benevolent Dictator For Life (SABDFL).

To his credit, he isn't pulling any punches or dancing around the question:

> **Why are you telling Amazon what I am searching for?**
> 
> We are not telling Amazon what you are searching for. Your anonymity is preserved because we handle the query on your behalf. Don't trust us? Erm, we have root. You do trust us with your data already. You trust us not to screw up on your machine with every update. You trust Debian, and you trust a large swathe of the open source community. And most importantly, you trust us to address it when, being human, we err.

One of the statements here is pretty ominous at first: "Don't trust us? Erm, we have root." Mark refers to the fact that system updates are all done as root, and they can indeed slip in any code they want in there, which could include a remote-administration trojan or a little script uploading all of `$HOME` to Canonical's servers... But doing so would go directly against their users and instantly ruin their reputation. It is expectable from users to trust their operating system vendor will not snoop on them. The argument, while technically correct, doesn't hold much water when considering user expectations and Canonical's own business interests.

However, I'd like to challenge one particular passage (emphasis mine):

> We are **not telling Amazon** what you are searching for. **Your anonymity is preserved** because we handle the query on your behalf.

There's a number of issues here.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## "We are not telling Amazon what you are searching for."

The way the search is handled goes as follows:

* User begins typing in the Dash search field
* An HTTP request (not HTTPS!) is made to a server called `productsearch.ubuntu.com`, containing the keywords
* `productsearch.ubuntu.com` asks Amazon's API for search results; to do so, it obviously needs to send the search terms. It is unknown whether that query is made over HTTPS or not.
* The search results are sent back to the client in a JSON string

The request looks like this:

	:::http
	GET /v1/search?q=test HTTP/1.1
	Host: productsearch.ubuntu.com
	Accept-Encoding: gzip, deflate
	User-Agent: gvfs/1.13.9
	Accept-Language: en-ca, en;q=0.9, en;q=0.8
	Connection: Keep-Alive

And the response:

	:::http
	HTTP/1.1 200 OK
	Date: Tue, 25 Sep 2012 07:17:39 GMT
	Server: gevent/0.13.0 gunicorn/0.13.4
	Vary: X-Geo-Country
	Content-Type: application/json
	Content-Length: 44674
	X-Cache: MISS from alkes.canonical.com
	X-Cache-Lookup: HIT from alkes.canonical.com:3128
	Via: 1.0 alkes.canonical.com:3128 (squid/2.7.STABLE7)
	Via: 1.1 productsearch.ubuntu.com
	Keep-Alive: timeout=15, max=100
	Connection: Keep-Alive
	
	...

Of course, it is trivial to see why the statement is wrong in the first place: `productsearch.ubuntu.com`&nbsp;*is* telling Amazon what you're searching for. What it is not telling is who you are, because (supposedly) the API request doesn't contain any identifying information other than your search terms.

This oversight is most likely just poor wording on Mr. Shuttleworth's part, though. What the sentence is really trying to say is: "We are telling Amazon what Ubuntu users are searching for, but we are not telling them who these users are."

That's fine, although it still raises some important privacy questions. Indeed, this search is performed when the user is using Unity's "Home" lens, which is where you can search for applications, files in your `$HOME` folder, and now Amazon search results. However, the documents in one's `$HOME` folder are usually fairly private. Even their filename alone usually speaks volumes (`Top-secret plan to kill my boss.doc`, `Confessions of a (fill in the blank).pdf`, `How to (fill in the blank).epub`, `credit-card-(some number).kmy`, etc.). They usually contain *people's names* in them, too. The search terms reveal a lot by themselves about the person typing them. Users are going to be searching for those files in the Home lens, because that is what they have always done and that is what they are used to. Unbeknownst to them, they are now sending these sensitive search terms **over plain HTTP** (visible to your local sysadmin, your boss (through your sysadmin), your ISP, and who knows, maybe your government (through subpoenas). And then Canonical sees it, and Amazon does too, and any other peer along the ride. The only thing that Canonical is doing is masking your IP address from Amazon.

The net result that Canonical claims: Canonical knows IPs and search terms, Amazon knows search terms. The only thing that Amazon doesn't know: Who is searching what.

Now, I'd like to question this claim by simply looking at the Wireshark output from running any search query. Try to do the following:

* Install Wireshark
* Start it and launch a capture
* Open the dash and type a few characters
* Check what Wireshark says

You'll see something like this:

	:::http
	GET /images/I/41Qemdr7ieL._SL160_.jpg HTTP/1.1
	Host: ecx.images-amazon.com
	Accept-Encoding: gzip, deflate
	User-Agent: gvfs/1.13.9
	Accept-Language: en-us, en;q=0.9
	Connection: Keep-Alive

And the response:

	:::http
	HTTP/1.0 200 OK
	Date: Mon, 24 Sep 2012 15:55:23 GMT
	Server: Server
	Cache-Control: max-age=630720000,public
	Expires: Wed, 18 May 2033 03:33:20 GMT
	Content-Length: 4630
	Last-Modified: Wed, 08 Aug 2012 22:34:21 GMT
	Content-Type: image/jpeg
	Age: 47375
	X-Cache: Miss from cloudfront
	X-Amz-Cf-Id: aBNnNXkOlBFeFzoYljLrLBE2MTi0TMmDIvZfbzslKOM-8V1Wi9T2sA
	Via: 1.0 574341a971a46a2980db13237b8175da.cloudfront.net (CloudFront)
	Connection: keep-alive
	
	...

This is simply the Dash downloading the thumbnails that accompany each search result. Each item in the dash has a prominent icon, and a label underneath:

[![Unity Dash thumbnail][]][Unity Dash]

Of course these images need to be downloaded from somewhere. Let's download them from the source, `images-amazon.com`! What could possibly go wrong? This goes against Mr. Shuttleworth's claim that Amazon doesn't know who is searching what. Indeed, while Amazon can't map search terms to IP addresses, what they can do is log the requests on their images server, and simply look at the name of the corresponding product and figure out what the search terms were. Or simply correlate them with a recent API query received from `productsearch.ubuntu.com`.

Some additional nitpicks:

* Those image requests are done over HTTP as well, even though Amazon provides an SSL version of their image service at `ssl-images-amazon.com`. Fixing it would be a simple one-line replace in the code. The gain from using SSL for image content isn't enormous, but if it's available, why not use it? Some may argue "for speed". I'd advise these people to try out the Unity Dash search by themselves, and get back to me about how fast it currently is. I doubt speed was a big concern.
* The request uses a fairly unique `User-Agent` header: `gvfs/1.13.9`. [GVFS] is a component of the [GNOME desktop] used for filesystem stuff, including mounting [WebDAV] shares and the like. Unity is likely using the GNOME library to perform these HTTP requests. However, I think there is little reason for that component to ever hit the `amazon-images.com` domain, other than because of the Unity Dash advertisements. As such, Amazon now has an easy way to identify which image requests result from a Unity Dash search.
* The request contains an `Accept-Language` header which contains the user's locale. It is set to `en-us, en` if you install the US English version of Ubuntu, but can be set to `fr` if you install the French language pack and set it as default, and so on. This isn't a huge information leak, but it gives Amazon more data to correlate the terms with, because you probably typed your search terms in that language. At any rate, it is *not necessary* for Amazon to know the language in order to serve static image files, so why tell them?

I have filed [a bug about all of these issues][Launchpad: Direct data leaking to Amazon].

So there we have it. Something which may have started from good intentions ("*Let's have the Dash search the web to provide users with richer search results!*") turned into something much worse ("*Let's put irrelevant revenue-generating advertisements on by default in a place where the user is likely to type private information and wouldn't expect that information to be sent out to anyone!*") through a series of oversights. This was pushed through [Ubuntu's Feature Freeze][Ubuntu Feature Freeze] period because it had executive support from the top people, and its release was rushed through with little regard to the users' interest (there was no warning that this was coming), or to the [PR disaster][Slashdot: Ubuntu Will Now Have Amazon Ads Pre-Installed] that was inevitably going to follow.

Oh, and did I mention that, privacy concerns aside, [advertisements in an operating system][United States Patent Application 20090265214] are not a good idea in the first place? It's an intrusion of the user's personal space, and it drowns the search results in [inconsistent][Launchpad: Capitalization of "More suggestions" doesn't match the rest of the dash], unnecessary, [inappropriate][Launchpad: No obvious way to restrict shopping suggestions from displaying adult products], slow-loading, [irrelevant][Launchpad: Searching for software in the Dash now suggests software that can not be used with Ubuntu] noise that sometimes *replaces* existing local search results. It's especially annoying when you're about to click on one of these, and suddenly what you're clicking on just turned into an ad.

For the record: I don't use Ubuntu personally, although I tend to recommend it to non-technically-inclined people who want to try out a Linux distribution. This whole easily-avoidable advertising mess would make me change my tune.

## How to fix it

So now that the damage has been done, how do we get things straightened out?

### Step 0: Reconsider

It's not too late to reconsider everything, and to dismiss the idea entirely. There's plenty of justification for that in this very post, or in the comments thread of the main [Launchpad bug report][Launchpad: Don't include remote searches in the home lens]. People won't forget what happened, but they will certainly appreciate such a decision because it means that their complaints have been heard.

### Step 1: Update your privacy policy

This is a no-brainer. If you're going to gather more data about your users than you previously did, you need to update the privacy policy.

Thankfully, there is already a [bug report about this][Launchpad: Inadequate disclosure of data-sharing], so this is on Canonical's radar.

### Step 2: Make things clear to users

Users don't read privacy policies. It's important to have one, but users won't read it. Yet, they need to be aware of what is happening to their own data. To this end, I propose the following solution:

* Whenever the current lens is going to communicate with the Internet, replace the looking glass icon in the text field by a globe icon.
* Whenever there is a web request actively going on, make the globe rotate (as opposed to the spinner animation currently in use for local searches).
* Whenever the globe icon is clicked, open a little panel explaining to the user the implications of the search they are about to make.

This makes it clear that there is something going on that will send data over the network, and it gives the user easy access to more detailed information about what exactly is going to happen.

Here's quick mockup of what this could look like (though it needs better fonts and icons):

[![Unity Dash disclosure mockup thumbnail][]][Unity Dash disclosure mockup]

Think this message sounds scary? That's true. But then again, so is sending sensitive search terms to various unrelated third parties.

### Step 3: Make it opt-in rather than opt-out

This is pretty self-explanatory. Any feature that goes against user expectations when enabled by default should be opt-in.

At the very least, it should be easy for the user to remove this feature. Currently, it isn't: The user needs to remove the `unity-lens-shopping` package:

	:::console
	$ sudo apt-get purge unity-lens-shopping

This is not user-friendly nor obvious. Canonical [plans to address this][Launchpad: No easy way to disable (results from) this lens], though they do not intend to make it opt-in at this time.

### Step 4 option A: Make your actual strategy match your intended one

The current strategy doesn't respect the privacy guarantees that Canonical wants to provide. To fix this, here is what needs to happen:

* Make the Dash use SSL/TLS when talking to `productsearch.ubuntu.com` (this is [already in Canonical's plans][Launchpad: Change from http to https and verify cert])
* Open up the source code used on the backend servers at `productsearch.ubuntu.com` (why not?)
* Make the request from `productsearch.ubuntu.com` to Amazon use SSL as well. There's no reason not to, and having both hops over SSL strengthens the guarantee that only Canonical and Amazon can see the search terms.
* Include the thumbnails of each item inside the reply from `productsearch.ubuntu.com` to the user. Use the `data` URI scheme to do that, or have the client request it by itself from `productsearch.ubuntu.com` (not Amazon), over SSL as well.

### Step 4 option B: Actually make search terms anonymous

There is a relatively easy solution for Canonical to provide full search terms anonymization, such that Canonical only knows the IP of Ubuntu users (but not what they're searching), and Amazon only knows what Ubuntu users are searching for (but not who is searching what).

To pull this off, all Canonical needs to do is to set up a relay server instead of the current web server at `productsearch.ubuntu.com`. That relay server would simply forward whatever it gets from a client to Amazon, and send everything it got from Amazon back to the original client.

The client would effectively be performing an Amazon API request directly, using SSL, and Canonical's server would simply forward the encrypted bits along. This way, Canonical doesn't get to see which search terms are sent, thus any logging they may do would be useless. Amazon would see the search terms, but the only IP they would get is the Canonical server's IP. Users would still need to be warned that they shouldn't type identifying information as search terms, so that Amazon cannot link those search terms back to the users.

One of the consequences of this approach is that `productsearch.ubuntu.com` could now easily become a publicly-available spam relay towards Amazon's API servers. While I doubt that Amazon's API could be brought down solely from traffic coming from a Canonical server (my guess is that the Canonical server would crash and burn long before this happens), such a situation could potentially be solved through abuse complaints from Amazon to Canonical, asking Canonical to block certain IPs from sending further requests.

The downside of this system, of course, is that Canonical doesn't get to see the search terms. They [claim they need to gather the search terms and click data][More Information About Online Dash Search Privacy] so that they can "provide better, more relevant results", in order to make the user experience better.

I have an alternative suggestion for Canonical to make the user experience better: Allow users to rate search results. Add a little section to the Dash under the Amazon results that asks "Were these results relevant?", and corresponding "Yes"/"No" buttons. The data from these buttons will be a more precise metric than the current metric: "whatever the user clicks is relevant".

And if you're telling yourself: "This will never work! Users will click 'No' all the time!", then perhaps you should ask yourself whether this feature was really made with the users' interest at heart in the first place.

[The Register: Fans revolt over Amazon 'adware' in Ubuntu desktop search results]: http://www.theregister.co.uk/2012/09/24/ubuntu_amazon_suggestions/
[Ars Technica: Ubuntu bakes Amazon search results into OS to raise cash]: http://arstechnica.com/business/2012/09/ubuntu-bakes-amazon-search-results-into-os-to-raise-cash/
[Launchpad: Don't include remote searches in the home lens]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054776
[Ubuntu]: http://www.ubuntu.com/
[Online Shopping Feature Arrives in Ubuntu 12.10]: http://www.omgubuntu.co.uk/2012/09/online-shopping-features-arrive-in-ubuntu-12-10
[Amazon affiliate program]: https://affiliate-program.amazon.com/
[Unity]: http://unity.ubuntu.com/
[Lots of Hype Over Shopping Lens in Ubuntu 12.10]: http://benjaminkerensa.com/2012/09/22/lots-of-hype-over-shopping-lens-in-ubuntu-12-10
[More Information About Online Dash Search Privacy]: http://www.jonobacon.org/2012/09/25/more-information-about-online-dash-search-privacy/
[Amazon search results in the Dash]: http://www.markshuttleworth.com/archives/1182
[Unity Dash thumbnail]: dash-thumbnail.png
[Unity Dash]: dash.png
[GVFS]: https://en.wikipedia.org/wiki/GVFS
[GNOME desktop]: https://en.wikipedia.org/wiki/GNOME_desktop
[WebDAV]: https://en.wikipedia.org/wiki/WebDAV
[Launchpad: Direct data leaking to Amazon]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1055952
[Ubuntu Feature Freeze]: https://wiki.ubuntu.com/FeatureFreeze
[Slashdot: Ubuntu Will Now Have Amazon Ads Pre-Installed]: http://yro.slashdot.org/story/12/09/22/1319216/ubuntu-will-now-have-amazon-ads-pre-installed
[United States Patent Application 20090265214]: http://www.freepatentsonline.com/y2009/0265214.html
[Launchpad: Capitalization of "More suggestions" doesn't match the rest of the dash]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054694
[Launchpad: No obvious way to restrict shopping suggestions from displaying adult products]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054282
[Launchpad: Searching for software in the Dash now suggests software that can not be used with Ubuntu]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1053678
[Launchpad: Inadequate disclosure of data-sharing]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054782
[Unity Dash disclosure mockup thumbnail]: dash-mockup-thumb.png
[Unity Dash disclosure mockup]: dash-mockup.png
[Launchpad: No easy way to disable (results from) this lens]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1054746
[Launchpad: Change from http to https and verify cert]: https://bugs.launchpad.net/ubuntu/+source/unity-lens-shopping/+bug/1055649