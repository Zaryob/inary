DESTDIR=/
all: build

clean:
	`find | grep pycache | sed 's/^/rm -rf /g'`
	rm -rf build
	rm -f po/*.mo
build:
	python3 setup.py build
install:
	python3 setup.py install --install-lib=${DESTDIR}/usr/lib/sulin --root=${DESTDIR}
	[ -f ${DESTDIR}/usr/bin/inary ] || ln -s inary-cli ${DESTDIR}/usr/bin/inary || true
