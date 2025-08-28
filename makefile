all: test

test:
	python3 -m doctest -v bibleg/__init__.py
