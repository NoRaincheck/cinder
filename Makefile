build:
	npx tweego@2.1.1 src -o dist/index.html
test:
	python3 -m pytest tests/ -v
