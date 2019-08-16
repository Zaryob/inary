.. -*- coding: utf-8 -*-

===========
inary check
===========

`inary check` komutu sisteme kurulu olan paketlerin detaylı analizini yapar. \
Kırılmış veya silinmiş bir içerik varsa veya değiştirilmiş bir config dosyası \
var ise bunu görmemizi sağlar.

**Yardım Çıktısı**
------------------

.. code-block:: shell

        $ inary check --help
        Kurulumu denetle

        Kullanım: check [<paket1> <paket2> ... <paketn>]
                  check -c <bileşen>\n"

        <paketi> : paket adı

        Yüklenen her dosya için bir kontrol toplamı tutulur. Check komutu
        paketin kurulumunun doğruluğunu kontrol etmek için bu
        toplamları kullanır. Paketlerin adlarını vermeniz yeterlidir.

        Eğer hiç paket adı verilmemişse, kurulu durumdaki bütün paketler
        doğrulanır.

        Seçenekler:
         --version                    : programın sürüm numarasını göster ve çık
         -h [--help]                  : bu yardım iletisini göster ve çık

         denetleme seçenekleri:
          -c [--component] arg        : Verilen bileşen altındaki kurulu paketleri
                                        denetle.
          --config                    : Paketlerin sadece değişen yapılandırma
                                        dosyalarını denetler.

         genel seçenekler:
          -D [--destdir] arg          : INARY komutları için sistem kökünü değiştir.
          -y [--yes-all]              : Bütün evet/hayır sorularında cevabı evet kabul
                                        et.
          -u [--username] arg
          -p [--password] arg
          -L [--bandwidth-limit] arg  : Bant genişliği kullanımını belirtilen kilobaytın
                                        altında tut.
          -v [--verbose]              : Detaylı çıktı
          -d [--debug]                : Hata ayıklama bilgisini göster.
          -N [--no-color]             : INARY çıktılarında renk kullanılmasını engeller.

**Örnek bir çalışma çıktısı**
-----------------------------

.. code-block:: shell

        $ inary check
        "acl" paketinin bütünlüğü denetleniyor         TAMAM
        "bash" paketinin bütünlüğü denetleniyor        TAMAM
        "unzip" paketinin bütünlüğü denetleniyor       TAMAM
        "tar" paketinin bütünlüğü denetleniyor         TAMAM
        $ inary check acl
        "acl" paketinin bütünlüğü denetleniyor        TAMAM
