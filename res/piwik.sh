#!/usr/bin/env bash

# Start configuration
PIWIK_DIR='/usr/share/webapps/piwik'
PIWIK_URL='http://127.0.0.1:51814/piwik/'
PIWIK_SITE='perot.me'
URL_EXCLUDES=(
	'/ping-ip'
	'/tt-rss'
	'/mozilla-sync'
	'/piwik' '/usr/share/webapps/piwik'
	'/robots.txt'
	'//(?:[-\w]+\.)*[-\w]+/.*MSIE 6' # MSIE 6 not supporting protocol-relative URLs; don't care
)
USERAGENT_EXCLUDES=(
	'Sogou web spider'
)
NGINX_LOG='/var/log/nginx/access.log.1' # Automatically adds .gz if necessary
LOG_FORMAT='(?P<host>[\w\-\.\/]*)(?::\d+)? (?P<ip>\S+) \S+ \S+ \[(?P<date>.*?) (?P<timezone>.*?)\] "\S+ (?P<path>.*?) \S+\" (?P<status>\S+) (?P<length>\S+) \"(?P<referrer>.*?)\" \"(?P<user_agent>.*?)\" \[DNT:-\]'
EXTRA_FLAGS=(--enable-http-errors --enable-http-redirects --enable-reverse-dns)
# End configuration

regexIsolate() {
	# Usage:
	#     regexIsolate regex cutoff-group replacement
	#         regex: The regular expression to cut
	#         cutoff-group: The name of the matching group to cut the regex at
	#         replacement: What to put right after the cut regex
	echo "$(echo "$1" | sed -r 's/\(\?P<'"$2"'>.*$//i')$3"
}

hostMatch='(?:\S*\.)?'"$(echo "$PIWIK_SITE" | sed 's/\./\\./g')"'\b'
hostnameRegex="$(regexIsolate "^$LOG_FORMAT" host "$hostMatch")"

excludePatterns=()
for exclude in "${URL_EXCLUDES[@]}"; do
	excludePatterns+=("$(regexIsolate "^$LOG_FORMAT" path "$exclude")")
done
for exclude in "${USERAGENT_EXCLUDES[@]}"; do
	excludePatterns+=("$(regexIsolate "^$LOG_FORMAT" user_agent "$exclude")")
done

recursiveUngrep() {
	local currentPattern
	currentPattern="$1"
	shift
	if [ "$#" -eq 0 ]; then
		grep -viP "$currentPattern"
	else
		grep -viP "$currentPattern" | recursiveUngrep "$@"
	fi
}

catnginx=(cat "$NGINX_LOG")
if [ -f "$NGINX_LOG.gz" ]; then
	catnginx=(zcat "$NGINX_LOG.gz")
elif [ -f "$NGINX_LOG.bz2" ]; then
	catnginx=(bzcat "$NGINX_LOG.bz2")
fi

exec "${catnginx[@]}" | grep -iP "$hostnameRegex" | grep '\[DNT:-\]$' | recursiveUngrep "${excludePatterns[@]}" | python2 "$PIWIK_DIR/misc/log-analytics/import_logs.py" --url="$PIWIK_URL" --hostname="$PIWIK_SITE" "${EXTRA_FLAGS[@]}" --log-format-regex="$LOG_FORMAT" -
