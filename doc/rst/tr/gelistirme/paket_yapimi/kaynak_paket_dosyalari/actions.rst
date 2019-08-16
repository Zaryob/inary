.. -*- coding: utf-8 -*-

Bu belgelendirme sayfası **actions.py** :term:`betik`'ine ait fonksiyonları içerir.

##################
**Actions** Nedir?
##################

Paket yöneticileri kaynak paket oluştururken derleme talimatlarını girdiğimiz dosyadır. \
Bu dosya bir python3 :term:`betik` dosyasıdır. İçerisindeki kütüphaneler `inary`_'ye ait python3 \
kütüphanesidir. `ActionsAPI`_ içerisindeki fonksiyonlar her çeşitte kaynak kodun inşaa \
ve kurulmasına uygun olarak yazılmıştır.

.. seealso: Dillere uygun `ActionsAPI`_ fonksiyonları için bknz. #Fixme:

 Inary paket yöneticisinde kaynak paketten ikili paket üretimi yapılırken \
bu dosya import edilir ve fonksiyonları çalıştırılır.


.. _inary: https://gitlab.com/Zaryob/inary/
.. _ActionsAPI: #Fixme:

Örnek bir `actions.py` dosyası şu şekildedir.

.. _target:

:file:`actions.py`

.. sourcecode:: python3

    #!/usr/bin/python
    # -*- coding: utf-8 -*-

    from inary.actionsapi import autotools
    from inary.actionsapi import inarytools
    from inary.actionsapi import get

    def setup():
        autotools.autoreconf("-fvi")
        autotools.configure("--disable-rpath \
                             --enable-utf8 \
                             --enable-altrcname \
                             --disable-speller")

    def build():
        autotools.make()

    def install():
        autotools.rawInstall("DESTDIR=%s" % get.installDIR())

        inarytools.insinto("/etc/", "doc/sample.nanorc", "nanorc")
        inarytools.dosym("/usr/bin/nano", "/bin/nano")

        inarytools.dohtml("doc/*.html")
        inarytools.dodoc("ChangeLog*", "README", "doc/sample.nanorc", "AUTHORS", "NEWS", "TODO", "COPYING*", "THANKS")

-------------------------------------------
**actions.py** :term:`betik`'inin fonksiyonları
-------------------------------------------

**actions.py** :term:`betik`'i paket talimatnamesi olarak kullanılır çünkü bu \
kaynak paket derleme işini adım adım yapabilmemize olanak verir. Her bir \
fonksiyon derlemenin bir adımını oluşturur.

******************
setup() fonksiyonu
******************
Paket derlemesinin ilk aşamasıdır. Paketin derleme öncesi dosyaları düzenlenir \
kaynak için `configure` işlemi burada yapılır.

.. note:: Configure işlemi öntanımlı olarak `/var/inary/<paket_adı>-<paket_sürümü>-<paket-yayımı>/work/` klasörü içinde yapılır

******************
build() fonksiyonu
******************
Kaynak kod bu kısımda inşaa edilir.

.. note:: Derleme işlemi öntanımlı olarak `/var/inary/<paket_adı>-<paket_sürümü>-<paket-yayımı>/work/` klasörü içinde yapılır

******************
check() fonksiyonu
******************
Derlenen kaynak kodun testi burada yapılır.

********************
install() fonksiyonu
********************
Derlenen kaynak kod paketleme klasörüne kurulur.

.. note:: Derlenen paketin kurulduğu öntanımlı paketleme klasörü `/var/inary/<paket_adı>-<paket_sürümü>-<paket-yayımı>/install/` klasörüdür
