DESTDIR=/
all: build install

clean:
	`find | grep pycache | sed 's/^/rm -rf /g'`
	rm -rf build
build:
	python3 setup.py build
install:
	python3 setup.py install --install-lib=${DESTDIR}/usr/lib/sulin
	install actions-main.c ${DESTDIR}/usr/lib/sulin/actions-main.c
	ln -s inary-cli ${DESTDIR}/usr/bin/inary || true
