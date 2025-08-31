all: test

test:
	python3 -m doctest -v bibleg/__init__.py

build:
	python3 -m build

upload: build
	python3 -m twine upload dist/*

format:
	python3 -m black bibleg/*.py

clean:
	rm -rf dist bibleg.egg-info
	rm -rf bibleg/__pycache__