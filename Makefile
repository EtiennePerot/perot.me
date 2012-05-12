# Dependencies:
#	rsync (https://rsync.samba.org/)
#	python (http://python.org/)
#	htmlcompressor (https://htmlcompressor.googlecode.com/)
#	Closure compiler (https://closure-compiler.googlecode.com/)
#	python-scss (http://packages.python.org/scss/)

SHELL = bash
SRC_DIR = src
BUILD_DIR = build
DEPLOY_URL = perot@perot.me:www-test
DEPLOY_PERMISSIONS = 750

all: clean build compress chmod deploy

build: build-init css js html

build-init:
	mkdir -p "$(BUILD_DIR)"
	rsync -rqhupXt --exclude=".git" --exclude="*.gz" --delete-after "$(SRC_DIR)/" "$(BUILD_DIR)/"

css:
	while IFS= read -d $$'\0' -r file ; do \
		echo Processing "$$file"; \
		pyscss -S "`dirname "$$file"`" "$$file" > "`echo "$$file" | sed 's/\.scss$$/.css/i'`"; \
	done < <(find "$(BUILD_DIR)" -name '*.scss' -print0)

js:
	# TODO

html:
	while IFS= read -d $$'\0' -r file ; do \
		if htmlcompressor --remove-intertag-spaces --simple-doctype --remove-style-attr --remove-script-attr --remove-form-attr --remove-js-protocol --remove-http-protocol --remove-https-protocol --compress-css --compress-js --js-compressor=closure --closure-opt-level=advanced < "$$file" > "$$file.compressed"; then \
			echo "Success compressing $$file"; \
			mv "$$file.compressed" "$$file"; \
		else \
			echo "Failed compressing $$file"; \
			rm -f "$$file.compressed"; \
		fi; \
		res/scss-import.py "$$file"; \
	done < <(find "$(BUILD_DIR)" \( -name '*.htm' -o -name '*.html' -o -name '*.xhtml' \) -type f -print0)

compress:
	while IFS= read -d $$'\0' -r file ; do \
		if [ ! -f "`echo "$$file" | sed 's/\.gz$$//i'`" ]; then rm -f "$$file"; fi;\
	done < <(find "$(BUILD_DIR)" -name '*.gz' -type f -print0)
	while IFS= read -d $$'\0' -r file ; do \
		if [ ! -f "$$file.gz" -o "$$file.gz" -ot "$$file" ]; then \
			echo gzip -cn9 < "$$file" > "$$file.gz"; \
			gzip -cn9 < "$$file" > "$$file.gz"; \
		fi; \
	done < <(find "$(BUILD_DIR)" ! -name '*.gz' -type f -print0)

chmod:
	chmod -R "$(DEPLOY_PERMISSIONS)" "$(BUILD_DIR)"

deploy:
	rsync -rzvvhupXct --exclude=".git" --delete-after --progress "$(BUILD_DIR)/" "$(DEPLOY_URL)/"

clean:
	rm -rf "$(BUILD_DIR)"
