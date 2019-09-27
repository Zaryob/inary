.. -*- coding: utf-8 -*-
.. _paket_yapimi_index:

%%%%%%%%%%%%%%%%%%%%%%%%%%
Kaynak Koddan Paket Yapımı
%%%%%%%%%%%%%%%%%%%%%%%%%%

Inary ikili paketleri kaynak kodlardan elde edilir. Kaynak kodlara ait tanımlamaları, derleme \
yönetmeliklerini, oluşturulacak ikili pakete ait tanım ve açıklamaların \
yerelleştirmelerini içerir.

Kaynak koddan paket üretimi için inary'de bazı dosyaların bulunması gerekmektedir. Derleme sırasında \
kullandığımız bu dosyalar bir dizin içerisine konulur. Bu dizin bizim kaynak paketimizi oluşturur. :

.. code-block:: text

    $ tree
    paket-adi/
        ├── pspec.xml
        ├── translations.xml
        ├── actions.py
        └── scom/
            └── betigin_adı.py


Paket derlemesi sırasında kullanılan dosyaları incelemek için bakınız.

    .. toctree::
       :name: kaynaktoc
       :maxdepth: 4

       kaynak_paket_dosyalari/index.rst

Adım adım paket yapım rehberi için bakınız.

    .. toctree::
       :name: derlemetoc
       :maxdepth: 2

       adim_adim_derleme_rehberi/index.rst
