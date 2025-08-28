all: test

test:
	python3 -m doctest -v bibleg/__init__.py

dist:
	python3 -m build

upload: dist
	python3 -m twine upload dist/*
