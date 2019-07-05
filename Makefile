PREFIX=/
all: build install

clean:
	`find | grep pycache | sed 's/^/rm -rf /g'`
	rm -rf build
build:
	python3 setup.py build
install:
	python3 setup.py install --prefix=$(PREFIX)
	install inary-cli $(PREFIX)usr/bin/inary
