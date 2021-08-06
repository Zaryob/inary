DESTDIR=/
all: clean build

clean:
	`find | grep pycache | sed 's/^/rm -rf /g'`
	rm -rf build
	rm -f po/*.mo

pot:
	xgettext --language=Python --keyword=_ --output=inary.pot \
            `find inary -type f -iname "*.py"` inary-cli
	for file in `ls po/*.po`; do \
	    msgmerge $$file inary.pot -o $$file.new ; \
	    rm -f $$file ; \
	    mv $$file.new $$file ; \
	done \

build:
	python3 setup.py build
install:
	mkdir -p ${DESTDIR}/usr/bin/ ${DESTDIR}/usr/lib/sulin || true
	python3 setup.py install --install-lib=${DESTDIR}/usr/lib/sulin --root=${DESTDIR} --install-scripts=${DESTDIR}/usr/bin
	[ -f ${DESTDIR}/usr/bin/inary ] || ln -s inary-cli ${DESTDIR}/usr/bin/inary || true
