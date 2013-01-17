# Dependencies:
#	rsync (https://rsync.samba.org/)
#	python (http://python.org/)
#	htmlcompressor (https://htmlcompressor.googlecode.com/)
#	Closure compiler (https://closure-compiler.googlecode.com/)
#	gifsicle (http://www.lcdf.org/gifsicle/)
#	inkscape (http://inkscape.org/)
#	png2ico (http://www.winterdrache.de/freeware/png2ico/)
#	Probably some others that I forgot

SHELL = bash
SRC_DIR = src
BUILD_DIR = build
STATIC_URL = /img
ASSETS_URL = $(STATIC_URL)/assets
STATIC_DIR = $(BUILD_DIR)$(STATIC_URL)
ASSETS_DIR = $(BUILD_DIR)$(ASSETS_URL)
DEPLOY_URL ?= perot@perot.me:www
DEPLOY_PERMISSIONS = 750
DEPLOY_PERMISSIONS_WRITABLE = 770
COMMENTS_QUEUE_DIR = blog/comments/queue
COMMENTS_NONCES_DIR = blog/comments/nonces
HTML_FILTERS_BEFORE_COMPRESSION ?= +process-exec +process-include +js-import +scss-import +resource-hash +duplicate-style
HTML_FILTERS_AFTER_COMPRESSION ?= +fix-openid +mark-compressed +free-js

all: clean build compress chmod deploy

build: build-init logo ajax blog css html cv

build-init:
	mkdir -p "$(BUILD_DIR)"
	rsync -rqhupXt --exclude=".git" --exclude="*.gz" --delete-after "$(SRC_DIR)/" "$(BUILD_DIR)/"

logo:
	# 16x16 logo is pregenerated, slightly different
	for w in 24 32 48 64 128 144 256 512; do \
		inkscape -z -e "$(STATIC_DIR)/logo/logo_$${w}x$${w}.png" -w "$$w" -h "$$w" "$(STATIC_DIR)/logo/logo.svg"; \
	done
	png2ico "$(BUILD_DIR)/favicon.ico" "$(STATIC_DIR)/logo/logo_16x16.png"

ajax:
	gifsicle -O3 -k 8 --color-method blend-diversity < "$(STATIC_DIR)/ajax.original.gif" > "$(STATIC_DIR)/ajax.gif"

blog:
	"$(BUILD_DIR)/blog/blog.py" --make

cv:
	cat "$(BUILD_DIR)/cv.md" | sed 's/ (at) /@/g' | sed 's/ (dot) /./g' | pandoc --latex-engine xelatex -V mainfont="Open Sans" -V linkcolor=black -V urlcolor=black -H "$(BUILD_DIR)/cv.sty" -o "$(BUILD_DIR)/cv.pdf"

css:
	while IFS= read -d $$'\0' -r file ; do \
		echo Processing "$$file"; \
		res/pyscss-monkeypatch.py -S "`dirname "$$file"`" -I "`dirname "$$file"`" -I "$(BUILD_DIR)" -A "$(ASSETS_DIR)" --static-root "$(BUILD_DIR)" --static-url "$(STATIC_URL)" --assets-url "$(ASSETS_URL)/" "$$file" > "`echo "$$file" | sed 's/\.scss$$/.css/i'`"; \
	done < <(find "$(BUILD_DIR)" -name '*.scss' -print0)

html:
	while IFS= read -d $$'\0' -r file ; do \
		echo "Processing $$file"; \
		res/filefilter.py $(HTML_FILTERS_BEFORE_COMPRESSION) "$$file"; \
		if htmlcompressor --preserve-php --remove-intertag-spaces --simple-doctype --remove-style-attr --remove-script-attr --remove-form-attr --remove-js-protocol --remove-https-protocol --compress-css --compress-js --js-compressor=closure --closure-opt-level=simple < "$$file" > "$$file.compressed"; then \
			mv "$$file.compressed" "$$file"; \
		else \
			rm -f "$$file.compressed"; \
			echo "Failed compressing $$file" 1>&2; \
		fi; \
		res/filefilter.py $(HTML_FILTERS_AFTER_COMPRESSION) "$$file"; \
	done < <(find "$(BUILD_DIR)" \( -name '*.htm' -o -name '*.html' -o -name '*.xhtml' -o -name '*.php' \) -type f -print0)

compress:
	while IFS= read -d $$'\0' -r file ; do \
		if [ ! -f "`echo "$$file" | sed 's/\.gz$$//i'`" ]; then rm -f "$$file"; fi;\
	done < <(find "$(BUILD_DIR)" -name '*.gz' -type f -print0)
	while IFS= read -d $$'\0' -r file ; do \
		if [ ! -f "$$file.gz" -o "$$file.gz" -ot "$$file" ]; then \
			gzip -cn9 < "$$file" > "$$file.gz"; \
		fi; \
	done < <(find "$(BUILD_DIR)" ! -name '*.gz' -type f -print0)

chmod:
	chmod -R "$(DEPLOY_PERMISSIONS)" "$(BUILD_DIR)"
	chmod -R "$(DEPLOY_PERMISSIONS_WRITABLE)" "$(BUILD_DIR)/$(COMMENTS_QUEUE_DIR)" "$(BUILD_DIR)/$(COMMENTS_NONCES_DIR)"

deploy:
	rsync -rzvvhupXct --exclude=".git" --exclude="$(COMMENTS_QUEUE_DIR)" --exclude="$(COMMENTS_NONCES_DIR)" --exclude-from=".gitignore" --delete-after --progress "$(BUILD_DIR)/" "$(DEPLOY_URL)/"

clean:
	rm -rf "$(BUILD_DIR)"
