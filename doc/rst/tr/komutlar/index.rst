.. -*- coding: utf-8 -*-

%%%%%%%%%%%%%%%
Inary Komutları
%%%%%%%%%%%%%%%

Inary paket yönetim sistemi son kullanıcının beklediği tüm komutları
içerdiği gibi kendine özel komutlara da sahiptir.

``inary help`` diyerek bütün komutları görebilirsiniz.

.. code-block:: shell

    $ inary help
    usage: inary [seçenekler] <komut> [parametreler]

    <komut> aşağıdakilerden birisi olabilir:

               add-repo (ar) - Depo ekle
                  blame (bl) - Paket sahibi ve yayım bilgisi
                  build (bi) - Verilen INARY paket(ler)ini inşa et
                       check - Kurulumu denetle
      configure-pending (cp) - Configure pending packages
           delete-cache (dc) - Önbellek dosyalarını temizle
                  delta (dt) - Delta paketleri yarat
           disable-repo (dr) - Depoyu pasifleştir
                 emerge (em) - INARY kaynak paketlerini depodan inşa et ve kur
             emergeup (emup) - INARY kaynak paketlerini depodan inşa et ve yükselt
            enable-repo (er) - Depoyu etkinleştir
                  fetch (fc) - Paket indir
                       graph - Paket ilişkilerinin grafiğini çıkar
                    help (?) - Verilen komutlar hakkında yardım görüntüler
                history (hs) - INARY işlemlerinin günlüğü
                  index (ix) - Index INARY files in a given directory
                        info - Paket bilgisini göster
                install (it) - INARY paket(ler)i kur
         list-available (la) - Depolardaki paketleri listele
        list-components (lc) - Bileşenleri listele
         list-installed (li) - Tüm kurulu paketlerin listesini bas.
            list-newest (ln) - Depolardaki en yeni paketleri listele
          list-orphaned (lo) - List orphaned packages
           list-pending (lp) - Bekleyen paketleri listele
              list-repo (lr) - Depoları listele
           list-sources (ls) - Müsait kaynakları listele
          list-upgrades (lu) - Yükseltilecek paketleri listele
            rebuild-db (rdb) - Veritabanlarını Yeniden İnşa Et
                 remove (rm) - INARY paketlerini kaldır
        remove-orphaned (ro) - Remove orphaned packages
            remove-repo (rr) - Depoları kaldır
                 search (sr) - Paket ara
            search-file (sf) - Dosya ara
            update-repo (ur) - Depo veritabanlarını güncelle
                upgrade (up) - INARY paketlerini güncelle

    Belirli bir komut hakkında yardım almak için "inary help <komut>" kullanınız.


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
      

Tüm Komutlar Hakkında
`````````````````````
.. toctree::
   :maxdepth: 2


    check.rst
    clean.rst
    configure-pending.rst
    delete-cache.rst
