.. -*- coding: utf-8 -*-

===========
inary graph
===========

`inary graph` komutu sisteme ekli depolar arasındaki bağımlılık haritasını çizer.

**Yardım Çıktısı**
------------------

            $ inary graph --help
            kullanım: Paket ilişkilerinin grafiğini çıkar

            Kullanım: graph [<paket1> <paket2> ...<paketn>]

            Verilen paketlerden başlayarak, bağımlılık ve paket çakışmalarını
            da dikkate alarak paket ilişkilerinin grafiğini çıkar. Öntanımlı olarak
            depo paketleri arasındaki ilişkileri çıkarır ve dosyayı graphviz
            biçiminde 'pgraph.dot' dosyasına yazar.


            Seçenekler:
             --version                    : programın sürüm numarasını göster ve çık
             -h [--help]                  : bu yardım iletisini göster ve çık

             graph seçenekleri:
              -r [--repository] arg       : Belli bir depoyu belirt.
              -i [--installed]            : Kurulu paketlerin grafiği
              --ignore-installed          : Kurulu paketleri gösterme.
              -R [--reverse]              : Ters bağımlılık grafiği çiz.
              -o [--output] arg           : Dot çıktı dosyası

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
            $ inary graph
            Depolardaki bütün paketlerin arasındaki ilişkiler çiziliyor.
