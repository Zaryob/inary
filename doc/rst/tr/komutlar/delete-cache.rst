.. -*- coding: utf-8 -*-
-----
inary delete-cache
-----

`inary delete-cache` inary'ye ait geçici dosyaları paket ve kaynak kod arşivlerini
işe yaramadığı zaman temizlememizi sağlayan komuttur.

**Yardım Çıktısı**
------------------

.. code-block:: shell

        $ inary delete-cache --help
        Kullanım: delete-cache

        Kaynaklar, paketler ve geçici dosyalar /var dizinine kaydedilir.
        Bu dosyalar uzun vadede çok yer kaplayabilir.

        Seçenekler:
         --version                    : programın sürüm numarasını göster ve çık
         -h [--help]                  : bu yardım iletisini göster ve çık

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

        $ inary delete-cache
        Paket önbelleği "/var/cache/inary/packages" temizleniyor...
        Kaynak arşivi önbelleği "/var/cache/inary/archives" temizleniyor...
        Geçici dizin "/var/inary" temizleniyor...
        Önbellek dosyası "/var/cache/inary/componentdb.cache" temizleniyor...
        Önbellek dosyası "/var/cache/inary/installdb.cache" temizleniyor...
        Önbellek dosyası "/var/cache/inary/packagedb.cache" temizleniyor...
        Önbellek dosyası "/var/cache/inary/groupdb.cache" temizleniyor...
        Önbellek dosyası "/var/cache/inary/sourcedb.cache" temizleniyor...
