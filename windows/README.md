# Windows Ekran Süresi Takip

Bu uygulama, Windows işletim sisteminde çalışan uygulamaların kullanım sürelerini takip etmenizi sağlar.

## Özellikler

- Anlık uygulama kullanım takibi
- Kategori bazlı kullanım istatistikleri
- Günlük, haftalık ve aylık istatistikler
- Gece/gündüz kullanım analizi
- Sistem tray entegrasyonu
- Modern ve kullanıcı dostu arayüz
- Günlük bazlı detaylı istatistik görüntüleme
- İstatistikleri Excel'e aktarma

## Gereksinimler

- Python 3.8 veya üzeri
- Windows 10 veya üzeri

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python ekran_takip.pyw
```

## Kullanım

- Uygulama başlatıldığında sistem tray'de bir ikon görünecektir
- İkona tıklayarak ana pencereyi açabilirsiniz
- Pencereyi kapattığınızda uygulama arka planda çalışmaya devam edecektir
- Uygulamayı tamamen kapatmak için sistem tray'den "Çıkış" seçeneğini kullanın
- "Günlük İstatistikler" sekmesinden istediğiniz günün detaylı istatistiklerini görüntüleyebilirsiniz
- İstatistikleri Excel dosyası olarak dışa aktarabilirsiniz

## Notlar

- Veriler CSV formatında saklanır ve günlük olarak güncellenir
- Uygulama otomatik olarak gece/gündüz kullanımını ayırt eder
- Yeni kategori oluşturduğunuzda seçili uygulama otomatik olarak o kategoriye eklenir 