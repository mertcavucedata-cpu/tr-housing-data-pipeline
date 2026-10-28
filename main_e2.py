"""Emlak ilanlari scraper (egitim amacli).

Kiralik konut ilanlarini sayfa sayfa ceker, temizler ve
CSV, Excel ve SQLite formatlarinda kaydeder.

Gereksinimler: requests, pandas, openpyxl
"""

import logging
import random
import sqlite3
import time
from contextlib import closing

import pandas as pd
import requests

URL_SABLONU = (
    "https://bff.emlakjet.com/pages/v2/listing-search"
    "?path=%2Fkiralik-konut&sayfa={sayfa}&language=tr"
    "&include=listing&view=web&filtreler=ilan-sayisi%3D50"
)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com",
}
TIMEOUT = 15
BEKLEME_MIN = 2
BEKLEME_MAX = 4
MAX_ART_ARDA_HATA = 3
CSV_DOSYASI = "ilanlar.csv"
EXCEL_DOSYASI = "ilanlar_ex.xlsx"
DB_DOSYASI = "ilanlarim.db"
TABLO_ADI = "ilanlar_tablosu"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def ilanlari_cek(max_sayfa=50):
    """Belirtilen sayfa sayisi kadar kiralik konut ilan verilerini ceker."""

    tum_ilanlar = []
    art_arda_hata = 0

    for sayfa in range(1, max_sayfa + 1):
        url = URL_SABLONU.format(sayfa=sayfa)

        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.encoding = "utf-8"

            if response.status_code != 200:
                log.error("Sayfa %s HATA (kod: %s)", sayfa, response.status_code)
                art_arda_hata += 1
                if art_arda_hata >= MAX_ART_ARDA_HATA:
                    log.error("Ust uste %s hata, islem durduruldu.", art_arda_hata)
                    break
                time.sleep(random.uniform(BEKLEME_MIN, BEKLEME_MAX))
                continue

            data = response.json()

            # Eksik veya null alanlara karsi guvenli erisim
            ilanlar = (
                ((data.get("critical") or {}).get("listing") or {}).get("cards")
                or []
            )

            # Bos sayfa, ilanlarin bittigi anlamina gelir
            if not ilanlar:
                log.info("Sayfa %s bos geldi, ilanlar bitti.", sayfa)
                break

            for ilan in ilanlar:
                features = ilan.get("features") or {}
                location = ilan.get("location") or {}
                price = ilan.get("price") or {}

                sehir = location.get("city") or ""
                ilce = location.get("district") or ""

                tum_ilanlar.append(
                    {
                        "baslik": ilan.get("title"),
                        "konum": f"{sehir}/{ilce}",
                        "oda": features.get("rooms"),
                        "m2": features.get("grossArea"),
                        "fiyat": price.get("amount"),
                    }
                )

            art_arda_hata = 0
            log.info("Sayfa %s basariyla cekildi (%s ilan).", sayfa, len(ilanlar))
            time.sleep(random.uniform(BEKLEME_MIN, BEKLEME_MAX))

        except (requests.exceptions.RequestException, ValueError) as e:
            log.error("Sayfa %s baglanti/veri hatasi: %s", sayfa, e)
            art_arda_hata += 1
            if art_arda_hata >= MAX_ART_ARDA_HATA:
                log.error("Ust uste %s hata, islem durduruldu.", art_arda_hata)
                break
            time.sleep(random.uniform(BEKLEME_MIN, BEKLEME_MAX))
            continue

    return tum_ilanlar


def disa_aktarma(tum_ilanlar):
    """Toplanan verileri CSV, Excel ve SQLite formatlarinda kaydeder."""

    if not tum_ilanlar:
        log.warning("Kaydedilecek veri bulunamadi!")
        return

    df = pd.DataFrame(tum_ilanlar)

    onceki = len(df)
    df = df.drop_duplicates()
    log.info("%s tekrar eden ilan silindi.", onceki - len(df))

    df.to_csv(CSV_DOSYASI, index=False, encoding="utf-8-sig")
    log.info("Veriler '%s' dosyasina yazildi.", CSV_DOSYASI)

    try:
        df.to_excel(EXCEL_DOSYASI, index=False)
        log.info("Veriler '%s' dosyasina yazildi.", EXCEL_DOSYASI)
    except (ImportError, OSError) as e:
        log.error("Excel kayit hatasi: %s", e)

    try:
        with closing(sqlite3.connect(DB_DOSYASI)) as baglanti:
            df.to_sql(TABLO_ADI, baglanti, if_exists="replace", index=False)
        log.info("Veriler '%s' veritabanina islendi.", DB_DOSYASI)
    except sqlite3.Error as e:
        log.error("Veritabani kayit hatasi: %s", e)


# --- Ana Calistirma Blogu ---
if __name__ == "__main__":
    log.info("Web scraping operasyonu baslatiliyor...")
    ilan_listesi = ilanlari_cek(50)
    disa_aktarma(ilan_listesi)
    log.info("Tum islemler tamamlandi!")