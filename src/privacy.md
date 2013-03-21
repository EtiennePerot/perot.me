This site uses a combination of [nginx]'s server logs and [Piwik] (in [log analytics mode][Piwik Server Log Analytics]) to gather and store traffic statistics.

No information is shared with third parties; this site does not use any third-party tracking resource whatsoever, with some temporary exceptions during [Internet Defense League] campaigns.

## nginx logs

### Data retention

[nginx] logs are [rotated][Log rotation] daily, and fall out of rotation after 7 days. Logs that fall out of rotation are deleted. They are not backed up.

### Data recorded

The logs contain the following information for every request sent to this domain:

* Full request URL and method
* Full [IP address] of the client
* Which website you were visiting before you clicked a link to this website ([HTTP Referer header])
* Which browser and operating system you use ([HTTP User-Agent header])
* Whether or not you have chosen to not be tracked ([HTTP Do Not Track header])
* Second-granularity request time
* Response status code and size of the response body

The exact line used for nginx's [`log_format`][nginx log_format] line can be found in [the nginx configuration file for this website][nginx configuration file].

## Piwik

### Data retention

[Piwik] traffic statistics are stored indefinitely.

All requests that have the [HTTP Do Not Track header] enabled are **not recorded**.

### Data recorded

Piwik traffic statistics contain the following information:

* Full request URL and method
* First two bytes of IPv4 addresses. IPv6 addresses are not truncated. If you would like to see this change, there is [a bug about this on the Piwik bug tracker][Piwik Bug Tracker: Anonymize IP does not mask IPv6 addresses].
* Which website you were visiting before you clicked a link to this website ([HTTP Referer header])
* Which browser and operating system you use ([HTTP User-Agent header])
* Second-granularity request time
* Response status code

## Opting out

If you would like your requests to be omitted from the Piwik traffic stats, simply [enable Do Not Track][Enable Do Not Track in Mozilla Firefox]. Requests that have the [HTTP Do Not Track header] will **not** be recorded.

nginx logs have no opt-out option, but only last for 7 days. If you would like to spoof some of the information they contain, here are some options you can use:

* [Tor] to anonymize your [IP address]
* [RefControl] to modify the [HTTP Referer header] on a per-website basis
* [UAControl] to modify the [HTTP User-Agent header] on a per-website basis

[nginx]: http://nginx.org/
[Piwik]: https://piwik.org/
[Piwik Server Log Analytics]: https://piwik.org/log-analytics/
[Internet Defense League]: http://internetdefenseleague.org/
[Log rotation]: https://en.wikipedia.org/wiki/Log_rotation
[IP address]: https://en.wikipedia.org/wiki/IP_address
[HTTP Referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[HTTP User-Agent header]: https://en.wikipedia.org/wiki/User_agent
[HTTP Do Not Track header]: https://en.wikipedia.org/wiki/Do_Not_Track
[nginx log_format]: http://wiki.nginx.org/HttpLogModule#log_format
[nginx configuration file]: https://github.com/EtiennePerot/perot.me/blob/master/nginx.conf
[Piwik Bug Tracker: Anonymize IP does not mask IPv6 addresses]: https://dev.piwik.org/trac/ticket/3710
[Enable Do Not Track in Mozilla Firefox]: https://support.mozilla.org/en-US/kb/how-do-i-turn-do-not-track-feature?redirectlocale=en-US&redirectslug=how-do-i-stop-websites-tracking-me
[Tor]: https://www.torproject.org/
[RefControl]: https://addons.mozilla.org/EN-US/firefox/addon/refcontrol/
[UAControl]: https://addons.mozilla.org/en-US/firefox/addon/uacontrol/
