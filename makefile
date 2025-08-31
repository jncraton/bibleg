all: test

test:
	python3 -m doctest -v bibleg/__init__.py

build:
	python3 -m build

upload: build
	python3 -m twine upload dist/*

format:
	python3 -m black bibleg/*.py

lint:
	python3 -m black --check bibleg/*.py
	python3 -m flake8 --max-line-length=88 bibleg/*.py

clean:
	rm -rf dist bibleg.egg-info
	rm -rf bibleg/__pycache__