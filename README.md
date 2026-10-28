# Emlak İlanı Scraper (Eğitim Amaçlı)

Bir emlak ilan platformunun listeleme verilerini sayfa sayfa çeken, temizleyen ve CSV, Excel ve SQLite formatlarında kaydeden Python scraper'ı.

> **Yasal not:** Bu proje yalnızca eğitim amaçlıdır. Herhangi bir sitenin verisini çekmeden önce o sitenin kullanım koşullarını ve `robots.txt` dosyasını kontrol etmek kullanıcının sorumluluğundadır. Çekilen veri ticari amaçla kullanılmamalı ve yeniden dağıtılmamalıdır.

## Özellikler

- Çok sayfalı veri çekme (sayfa sayısı ayarlanabilir)
- Rastgele bekleme süreleri ve zaman aşımı (timeout)
- Art arda 3 hatada programı güvenle durdurma
- Eksik veya boş (null) alanlara karşı korumalı veri okuma
- Boş sayfa geldiğinde otomatik durma
- Tekrar eden ilanların temizlenmesi
- Çıktı: **CSV**, **Excel (.xlsx)** ve **SQLite**
- Tüm işlemlerin `scraper.log` dosyasına kaydı

## Çekilen Alanlar

`baslik`, `konum`, `oda`, `m2`, `fiyat`

<!-- Sütun adlarını kendi son sürümüne göre güncelle -->

## Kullanılan Teknolojiler

Python 3, `requests`, `pandas`, `openpyxl`, `sqlite3`, `logging`

## Kurulum ve Çalıştırma

```bash
pip install requests pandas openpyxl
python emlak_scraper.py
```

## Sürüm Geçmişi

- **v1:** Temel sürüm (`print` ile çıktı)
- **v2:** Hata yönetimi, timeout, logging, tekrar temizleme ve Excel çıktısı eklendi
