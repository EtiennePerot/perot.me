#!/bin/zsh

set -euxo pipefail

if [[ -z "$TALOSROOT" ]] || [[ ! -d "$TALOSROOT" ]]; then
	echo 'Must define TALOSROOT environment variable.' >&2
	exit 1
fi

talos1="$TALOSROOT/The Talos Principle - Time Capsules from Alexandra Drennan [bmqA3pGe3Og].webm"
talos1w="$TALOSROOT/The Talos Principle - Full Game Walkthrough [All Endings] [y2qrccEW1hE].webm"
talos2="$TALOSROOT/The Talos Principle 2 - Full Game Walkthrough (No Commentary) - 100% Achievements [Part 1⧸2] [hXvJEj1cuGw].webm"
talos22="$TALOSROOT/The Talos Principle 2 - Full Game Walkthrough (No Commentary) - 100% Achievements [Part 2⧸2] [VDQZh7N3KKk].webm"
postroot="$(dirname "$0")"
maxjobs=1

tmptalos1=/tmp/timecaps.webm
if [[ ! -e "$tmptalos1" ]]; then
	ln -s "$talos1" "$tmptalos1"
fi

waitforjobs() {
	while test "$(jobs | wc -l)" -ge "$1"; do sleep 1; done 
}

loudnorm_opts() {
	local data
	local input_i
	local input_lra
	local input_thresh
	local input_tp
	data="$(ffmpeg -i "$1" -filter:a loudnorm=print_format=json -vn -sn -dn -f null /dev/null </dev/null 2>&1 | grep -P '^\s*"(input_i|input_lra|input_tp|input_thresh)"\s*:\s*"[^"]+"' | sed -r 's/^\s*"([^"]+)"\s*:\s*"([^"]+)".*$/\1:\2/')"
	input_i="$(echo "$data" | grep -P '^input_i:' | cut -d':' -f2)"
	input_lra="$(echo "$data" | grep -P '^input_lra:' | cut -d':' -f2)"
	input_tp="$(echo "$data" | grep -P '^input_tp:' | cut -d':' -f2)"
	input_thresh="$(echo "$data" | grep -P '^input_thresh:' | cut -d':' -f2)"
	echo -n "linear=true:measured_I=$input_i:measured_LRA=$input_lra:measured_tp=$input_tp:measured_thresh=$input_thresh"
}

normalize_audio() {
	local AUDIO_OPTIONS
	mv "$1" "$1.tmp"
	AUDIO_OPTIONS=()
	if echo "$1" | grep -P '\.webm$'; then
		AUDIO_OPTIONS=(-acodec libopus -ab 92k -ac 2)
	else
		AUDIO_OPTIONS=(-acodec aac -ab 92k -ac 2 -tag:v hvc1)
	fi
	ffmpeg -i "$1.tmp" -sn -vcodec copy -af "loudnorm=$(loudnorm_opts "$1.tmp"),aresample=48000" "${AUDIO_OPTIONS[@]}" "$1"
	rm "$1.tmp"
}

for format in webm mp4; do
	VIDEO_OPTIONS=()
	if [[ "$format" == webm ]]; then
		VIDEO_OPTIONS=(-vcodec libsvtav1 -crf 37 -acodec flac -ac 2 -f matroska)
		VIDEO_OPTIONS_PROMETHEUS=(-vcodec libsvtav1 -crf 39 -acodec flac -ac 2 -f matroska)
	else
		VIDEO_OPTIONS=(-vcodec libx265 -crf 26 -preset veryslow -acodec flac -ac 2 -tag:v hvc1)
		VIDEO_OPTIONS_PROMETHEUS=(-vcodec libx265 -crf 26 -preset veryslow -acodec flac -ac 2 -tag:v hvc1)
	fi

	waitforjobs "$maxjobs"; (
		ffmpeg -ss 8:27 -copyts -i "$talos1" -ss 8:27 -vf subtitles="$tmptalos1":force_style='Fontsize=24pt' -t $(( 48-28 )).5 -sn "${VIDEO_OPTIONS[@]}" -y "$postroot/intelligence.$format"
		normalize_audio "$postroot/intelligence.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss 8:47 -copyts -i "$talos1" -ss 8:47 -vf subtitles="$tmptalos1":force_style='Fontsize=24pt' -t $(( 60-47+43 )) -sn "${VIDEO_OPTIONS[@]}" -y "$postroot/values.$format"
		normalize_audio "$postroot/values.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss 34 -copyts -i "$talos1" -ss 34 -vf subtitles="$tmptalos1":force_style='Fontsize=24pt' -t $(( 68 - 34)) -sn "${VIDEO_OPTIONS[@]}" -y "$postroot/play.$format"
		normalize_audio "$postroot/play.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 4*3600 + 3*60 + 26 )).15 -t $(( (8-3)*60 )) -i "$talos1w" -sn -vf "scale=-1:640" "${VIDEO_OPTIONS[@]}" -y "$postroot/talos_principle_ending.$format"
		normalize_audio "$postroot/talos_principle_ending.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss  $(( 0 * 3600 + 14*60 + 27 )) -t $(( ( 15 - 14 ) * 60 + ( -2 ) )).05 -i "$talos2" -ss $(( 31 * 60 + 23 )) -t $(( 120 + 5 )).9 -i "$talos2" -ss $(( 35 * 60 + 21 )).15 -t $(( 34 - 21 )).5 -i "$talos2" -ss $(( 25*60 + 49 )).15 -t $(( 38-49+60 )).75 -i "$talos2"  -ss $(( 27*60 + 54 )).9 -t $(( 16.95 )) -i "$talos2" -ss $(( 47 * 60 + 44 )).65 -t $(( 60-44 + 6 )).5 -i "$talos2" -ss $(( 54 * 60 + 53 )).5 -t $(( 6 + 58 )).75 -i "$talos2" -filter_complex "[0:0][0:1][1:0][1:1][2:0][2:1][3:0][3:1][4:0][4:1][5:0][5:1][6:0][6:1]concat=n=7:v=1:a=1[out];[out]scale=-1:640" -r 60 "${VIDEO_OPTIONS[@]}" -y "$postroot/decels.$format"
		normalize_audio "$postroot/decels.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 18*60+14 )) -t $(( 1*60 + 30-14 )) -i "$talos2" -ss $(( 28*60+30 )).2 -t $(( 2*60+21-30.2 )) -i "$talos2" -filter_complex "[0:0][0:1][1:0][1:1]concat=n=2:v=1:a=1[out];[out]scale=-1:640" -r 60 "${VIDEO_OPTIONS[@]}" -y "$postroot/maintenance.$format"
		normalize_audio "$postroot/maintenance.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 16*60+24.5 )) -t $(( 1*60+13.35-24.5 )) -i "$talos2" -ss $(( 21*60+36 )) -t $(( 3*60-36+4 )) -i "$talos2" -ss $(( 3600+37*60+0.75 )) -t $(( 30.5-0.75 )) -i "$talos2" -filter_complex "[0:0][0:1][1:0][1:1][2:0][2:1]concat=n=3:v=1:a=1[out];[out]scale=-1:640" -r 60 "${VIDEO_OPTIONS[@]}" -y "$postroot/expedition.$format"
		normalize_audio "$postroot/expedition.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 3 * 3600 + 52 * 60 + 57 )) -i "$talos22" -vf scale=-1:640 -t $(( ( 54 - 52 ) * 60 + ( 59 - 57 ) )).7 -r 60 "${VIDEO_OPTIONS_PROMETHEUS[@]}" -y "$postroot/prometheus.$format"
		normalize_audio "$postroot/prometheus.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 2 * 3600 + 26 * 60 + 56 )).5 -i "$talos2" -r 60 -vf scale=-1:640 -t $(( ( 29 - 26 ) * 60 + ( -55+15 ) )) "${VIDEO_OPTIONS[@]}" -y "$postroot/sphinx.$format"
		normalize_audio "$postroot/sphinx.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 2 * 3600 + 34*60 + 18 )) -t $(( ( 35 - 34 ) * 60 + ( 0 ) )).25 -i "$talos2" -ss $(( 4 * 3600 + 17*60 + 21 )).85 -t $(( ( 18 - 17 ) * 60 + ( 34-22 ) )).15 -i "$talos2" -ss $(( 4 * 3600 + 56*60 + 02 )) -t $(( ( 0 ) * 60 + ( 29 ) )) -i "$talos2" -filter_complex "[0:0][0:1][1:0][1:1][2:0][2:1]concat=n=3:v=1:a=1[out];[out]scale=-1:640" -r 24 "${VIDEO_OPTIONS[@]}" -y "$postroot/audio_logs.$format"
		normalize_audio "$postroot/audio_logs.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 3600 + 52*60  + 38.6 )) -t $(( 60 - 38.6 + 45.75 )) -i "$talos2" -ss $(( 3*3600 + 40*60 + 31.75 )) -t $(( 60 - 31.75 + 14 )) -i "$talos2" -ss $(( 5*3600 + 0*60 + 28.65 )) -t $(( 2*60 - 28.65 + 17.55 )) -i "$talos2" -ss $(( 4*3600 + 37*60 + 48 )) -t $(( ( 42 - 37 )*60 - 48 + 36.1 )) -i "$talos2" -filter_complex "[0:0][0:1][1:0][1:1][2:0][2:1][3:0][3:1]concat=n=4:v=1:a=1[out];[out]scale=-1:640" -r 60 "${VIDEO_OPTIONS[@]}" -y "$postroot/humanity_is_precious.$format"
		normalize_audio "$postroot/humanity_is_precious.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss  $(( 3 * 3600 + 50*60 + 19 )).45 -t $(( ( 1 ) * 60 + ( 34 - 19 ) )).05 -i "$talos2" -vf "scale=-1:640,fade=out:st=72.5:d=2.5" -af 'afade=out:st=72.5:d=2.5' -r 60 "${VIDEO_OPTIONS[@]}" -y "$postroot/the_talos_principle.$format"
		normalize_audio "$postroot/the_talos_principle.$format"
	)

	waitforjobs "$maxjobs"; (
		ffmpeg -ss $(( 5 * 3600 + 23 * 60 + 31 )) -i "$talos2" -r 60 -vf scale=-1:640 -t $(( ( 24 - 23 ) * 60 + ( 38 - 31 ) )) "${VIDEO_OPTIONS[@]}" -y "$postroot/pandora.$format"
		normalize_audio "$postroot/pandora.$format"
	)

	wait
done
