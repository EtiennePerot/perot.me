#!/usr/bin/env bash

OLD_BUILD_DIR=old-build
BUILD_DIR=build

scriptDir="$(dirname "$BASH_SOURCE")"
rootDir="$(dirname "$scriptDir")"
cd "$rootDir"
enableCopy=''
if [ -d "$OLD_BUILD_DIR" -a -d "$BUILD_DIR" ]; then
	enableCopy='true'
fi

# Remove orphan .gz's
while IFS= read -d $'\0' -r file ; do
	if [ ! -f "$(echo "$file" | sed 's/\.gz$//i')" ]; then
		rm -f "$file"
	fi
done < <(find "$BUILD_DIR" -name '*.gz' -type f -print0)

fileList=()
while IFS= read -d $'\0' -r file ; do
	fileList+=("$file")
done < <(find "$BUILD_DIR" ! -name '*.gz' -type f -print0)
readarray -t sortedList < <(printf '%s\0' "${fileList[@]}" | sort -z | xargs -0n1)

toCompress=()
for file in "${sortedList[@]}"; do
	if [ ! -f "$file.gz" -o "$file.gz" -ot "$file" ]; then
		# File needs compression
		buildlessFile="$(echo "$file" | sed "s#^$BUILD_DIR/##")"
		oldBuiltFile="$OLD_BUILD_DIR/$buildlessFile"
		if [ -n "$enableCopy" -a -f "$oldBuiltFile" -a -f "$oldBuiltFile.gz" ]; then
			if [ "$(sha512sum "$file" | cut -d ' ' -f 1)" == "$(sha512sum "$oldBuiltFile" | cut -d ' ' -f 1)" ]; then
				echo "Copying '$oldBuiltFile.gz' to '$file.gz'"
				cp -a "$oldBuiltFile.gz" "$file.gz" || exit 1
				touch -r "$file" "$file.gz"
			else
				echo "Will compress '$file' (old version exists, but differs from current version)"
				toCompress+=("$file")
			fi
		else
			echo "Will compress '$file' (new file)"
			toCompress+=("$file")
		fi
	fi
done
for file in "${toCompress[@]}"; do
	echo "Compressing '$file'..."
	zopfli --i1000 "$file" || exit 1
	touch -r "$file" "$file.gz"
done
