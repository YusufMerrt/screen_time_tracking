Günlük İstatistik Uygulaması

Bu proje, kullanıcıların günlük ekran sürelerini izlemelerine ve analiz etmelerine olanak tanıyan bir istatistik uygulamasıdır. Program, kullanıcıların belirli bir tarihteki uygulama kullanım detaylarını görmesini sağlar ve çeşitli grafiksel görselleştirmeler sunar.

Öne Çıkan Özellikler

Günlük Verilerin Yüklenmesi:

Kullanıcılar belirli bir tarihi seçebilir ve o güne ait ekran süresi verilerini görebilir.

Tarih verileri CSV dosyasından dinamik olarak yüklenir.

Tarih Seçim Arayüzü:

Kullanıcıların mevcut verilerden tarih seçmesi için bir tarih seçici (ComboBox) bulunmaktadır.

Tarih bilgisi en son tarihe göre sıralanır ve varsayılan olarak en yeni tarih seçilir.

Grafiksel Analizler:

Günlük Kategori Dağılımı: Kullanıcının ekran süresinin farklı kategorilerde (ör. Sosyal Medya, Eğlence, İş) nasıl dağıldığını gösteren bir pasta grafiği.

En Çok Kullanılan Uygulamalar: Kullanıcının en çok zaman harcadığı 5 uygulamayı gösteren yatay çubuk grafik.

Gece/Gündüz Kullanımı: Gece ve gündüz kullanımlarının oranlarını karşılaştıran bir çubuk grafik.

Dinamik Veri İşleme:

Veriler pandas kütüphanesi ile okunur ve işlenir.

Uygulama, veri eksikliği durumunda kullanıcıyı bilgilendirir.

Kullanıcı Dostu Arayüz:

Veriler ve grafikler, kullanıcı dostu bir Tkinter tabanlı arayüzde görselleştirilir.

Teknik Detaylar

Kullanılan Teknolojiler

Python: Ana programlama dili.

Tkinter: Kullanıcı arayüzü tasarımı.

Matplotlib: Grafik çizimi.

Pandas: Veri işleme ve analizi.

Dosya Yapısı

ekran_suresi_takip.csv: Uygulama kullanım verilerini içeren CSV dosyası.

main.py: Uygulamanın ana kod dosyası.

CSV Dosya Formatı

CSV dosyasının şu sütunları içermesi beklenir:

Tarih: Verinin ait olduğu tarih (YYYY-AA-GG formatında).

Saat: Uygulama kullanımının başladığı saat.

Kategori: Uygulamanın ait olduğu kategori (ör. Sosyal Medya, İş).

Uygulama: Kullanılan uygulamanın adı.

Süre (Saat): Uygulamanın ne kadar süreyle kullanıldığı (saat cinsinden).

Kurulum ve Çalıştırma

Gerekli Kütüphaneleri Yükleyin:

Gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırın:

pip install -r requirements.txt

CSV Dosyasını Hazırlayın:

ekran_suresi_takip.csv dosyasını, yukarıda belirtilen formatta doldurun ve proje dizinine yerleştirin.

Uygulamayı Çalıştırın:

Ana Python dosyasını çalıştırarak uygulamayı başlatın:

python main.py

Grafiksel Analizlerin Detayları

1. Günlük Kategori Dağılımı (Pasta Grafiği)

Açıklama: Kullanıcıların ekran sürelerini hangi kategorilerde harcadığını gösterir.

Dinamik Özellikler:

Her kategoriye göre yüzdelik oranları hesaplar.

Yüzdesi %1'in altında olan kategoriler ayrı ayrı işaretlenir.

2. En Çok Kullanılan Uygulamalar (Yatay Çubuk Grafik)

Açıklama: Kullanıcıların en çok zaman harcadığı uygulamaları gösterir.

Dinamik Özellikler:

En çok kullanılan ilk 5 uygulamayı sıralar ve görselleştirir.

3. Gece/Gündüz Kullanımı (Çubuk Grafik)

Açıklama: Kullanıcının gece (00:00-11:59) ve gündüz (12:00-23:59) kullanım sürelerini karşılaştırır.

Dinamik Özellikler:

Verileri saat dilimlerine göre böler.

Eksik veri durumunda varsayılan değerler ile çalışır.

Hata Yönetimi

Tarih Seçim Hatası: Tarih seçilmediğinde kullanıcıya uyarı mesajı gösterilir.

Veri Eksikliği: Seçili tarihe ait veri bulunmuyorsa, kullanıcı bilgilendirilir.

Dosya Hataları: CSV dosyasına erişilemediğinde hata mesajı konsola yazdırılır.

Gelecek Geliştirmeler

Çoklu dil desteği eklenmesi.

Daha fazla grafik türü ile analiz seçenekleri.

Verilerin doğrudan uygulama içinde düzenlenebilmesi.

Kullanıcıların manuel veri girişi yapabileceği bir arayüz.

Ekran Görüntüsü

Grafikler ve arayüz, kullanıcı dostu ve sade bir tasarıma sahiptir. Çalıştırıldığında şu şekilde görünür:

Örnek Görselleştirme:

Günlük kategori dağılımı pasta grafiği.

En çok kullanılan uygulamalar çubuk grafiği.

Gece ve gündüz ekran süresi karşılaştırması.
