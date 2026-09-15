TWEEGO := build/tweego/tweego

.PHONY: build test

build: $(TWEEGO)
	mkdir -p dist
	$(TWEEGO) src -o dist/index.html

$(TWEEGO):
	tools/setup-tweego.sh

test:
	python3 -m pytest tests/ -v
