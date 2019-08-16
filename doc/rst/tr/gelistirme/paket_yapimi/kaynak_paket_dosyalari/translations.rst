.. -*- coding: utf-8 -*-

Bu belgelendirme sayfası **translations.xml** dosyasına ait XML dizin ağacını ve bu dosyanın kullanım inceliklerini içerir.

#######################
**Translations** nedir?
#######################

`SpecFile`_ içerisindeki `Summary`_ ve `Description`_ verilerini içeren dosyadır. \
Aslında ana dizin ağacı `SpecFile`_'a benzemektedir.

_SpecFile: #Fixme:
_Summary:
_Description:

Sadece `Source`_ ve `Package`_ ana :term:`etiket`'lerini ve bu :term:`etiket`'lere ait \
`Summary`_ ve `Description`_ alt :term:`etiket`'lerini içeren basit bir **pspec.xml** dosyasıdır

Aşağıda örnek bir **translations.xml** dosyası verilmiştir.

.. _target:

:file:`translations.xml`

.. sourcecode:: xml
    <INARY>
        <Source>
            <Name>nano</Name>
            <Summary xml:lang="tr">Konsol ortamında kullanabileceğiniz bir metin düzenleyicidir.</Summary>
            <Description xml:lang="tr">Nano özgür olmayan Pine paketinin içindeki metin düzenleme programı olan Pico'nun yerine geçme hedefini güden küçük, özgür ve kullanışlı bir metin düzenleme programıdır. Pico'nun görünüşünü ve işlevini kopyalamaktan çok, Nano aynı zamanda &quot;ara ve değiştir&quot; ve &quot;satır numarasına git&quot; gibi Pico'da olmayan (veya ön tanımlı olarak kapalı) bazı özellikleri sunar.</Description>
            <Description xml:lang="fr">Nano est un petit éditeur libre et convivial qui a pour but de remplacer Pico, l'éditeur par défaut inclus dans le paquet non-libre Pine. Plutôt que juste copier l'apparence et le ressenti de Pico, nan implémente également certaines fonctionnalité manquantes (ou désactivées par défaut), tel que &quot;rechercher et remplacer&quot; ou &quot;allez à la ligne numéro&quot;.</Description>
        </Source>
    </INARY>

Anlayacağınız üzere önceki belgelendirme sayfasında belirttiğimiz **xml:lang** \
:term:`belirteç`'i içerisine farklı dil bilgisi girilip `Summary`_ ve `Description`_ \
alt :term:`etiket`'lerine çeviriler eklenerek farklı dillerde Linux kullanan son kullanıcılara \
uygun tanımlama ve açıklamalar ulaştırılabilir ve İngilizce dil öğrenme zahmetine katlanmaktan \
kurtulunabilir.

.. seealso: Yerelleştirme için bakınız. #Fixme:
