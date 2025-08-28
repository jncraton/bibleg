all: test

test:
	python3 -m doctest -v bibleg/__init__.py

build:
	python3 -m build

upload: build
	python3 -m twine upload dist/*
