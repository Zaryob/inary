PREFIX=/
all: build install

clean:
	rm -rf build
build:
	python3 setup.py build
install:
	python3 setup.py install --prefix=$(PREFIX)
	install inary-cli $(PREFIX)usr/bin/inary
