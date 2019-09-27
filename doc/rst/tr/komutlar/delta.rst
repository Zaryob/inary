.. -*- coding: utf-8 -*-

===========
inary delta
===========

`inary delta` komutu ikili paketlerin iki farklı sürümünün dosyalarını \
karşılaştırarak sadece değişen dosyalardan oluşan bir delta paketi yaratır.

Bu bize güncelleştirmelleri küçültmemizi ve veri ağını daha az ve düzenli \
kullanmamızı sağlar.

**Yardım Çıktısı**
------------------

.. code-block::shell

            $ inary delta --help
            kullanım: Delta paketleri yarat

            Kullanım: delta eskipaket1 eskipaket2 ...  yenipaket
                      delta -t yenipaket eskipaket1 eskipaket2 ...

            Delta komutu, verilen paketlerde dosyaların sha1 toplamlarını
            karşılaştırarak değişen dosyaları bulur ve bu dosyaları
            içeren bir delta paketi oluşturur.


            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             delta seçenekleri:
              -t [--newest-package] arg   : Yeni paket adı olarak arg'ı kullan ve diğer
                                            argümanları eski paket listesi olarak al.
              -O [--output-dir] arg       : Üretilen paketler için çıktı dizini.
              -F [--package-format] arg   : İkili paketi verilen biçimde oluştur.
                                            Desteklenen biçimlerin listesini görmek için '-F
                                            help' kullanın.

             genel seçenekler:
              -D [--destdir] arg          : INARY komutları için sistem kökü dizinini
                                            değiştir.
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

.. code-block::shell

            $ inary delta expat-2.2.6-1-s19-x86_64.inary expat-2.2.6-2-s19-x86_64.inary
            Delta paketi oluşturuluyor: "expat-1-2-s19-x86_64.delta.inary"...
