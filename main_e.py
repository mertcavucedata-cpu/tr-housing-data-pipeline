import random
import time
import requests
import pandas as pd
import sqlite3

def ilanları_cek(max_sayfa=50):
    """ Web sitesinden belirtilen sayfa sayısı kadar kiralık konut ilan verilerini çeker"""
    
    headers = {
        "User-Agent":(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
        ),
        "Accept-Language":"tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer":"https://www.google.com"
    }

    tum_ilanlar = []
    for sayfa in range(1, max_sayfa + 1):
        url = f"https://bff.emlakjet.com/pages/v2/listing-search?path=%2Fkiralik-konut&sayfa={sayfa}&language=tr&include=listing&view=web&filtreler=ilan-sayisi%3D50"
        
        try:
            # 1. Güvenlik katmanı: Ağ ve bağlantı hatalarını yakalama.
            response = requests.get(url, headers=headers)
            response.encoding = "utf-8"

            if response.status_code == 200:
                data = response.json()
                ilanlar = data["critical"]["listing"]["cards"]
                
                for ilan in ilanlar:
                    try:
                        ## 2. Güvenlik Katmanı: Json etiketlerinde eksiklik çıkarsa çökmemesi için.
                        baslik = ilan.get("title")
                        fiyat = ilan.get("price", {}).get("amount")
                        metrekare = ilan.get("features", {}).get("grossArea")
                        oda = ilan.get("features", {}).get("rooms")
                        sehir = ilan.get("location", {}).get("city")
                        ilce = ilan.get("location", {}).get("district")
                        tum_ilanlar.append(
                            {
                                "Baslik": baslik,
                                "Sehir": sehir,
                                "Ilce": ilce,
                                "Oda_Sayisi": oda,
                                "Metrekare": metrekare,
                                "Fiyat": fiyat,
                            }
                        )
                    except (KeyError, AttributeError):
                        # Tek bir ilan verisi eksikse döngüyü kırmadan pas geçer
                        continue
                    
                print(f"{sayfa}. sayfa başarıyla çekildi ve sepete eklendi.")
                time.sleep(random.uniform(2, 4))
            else:
                print(f"HATA!! (code:{response.status_code})")
            
        except requests.exceptions.RequestException as e:
              print(f"Bağlantı hatası oluştu ({sayfa}. sayfa): {e}")
              continue
    
    return tum_ilanlar  

def disa_aktarma(tum_ilanlar):
    """Toplanan verileri Pandas ile CSV ve SQLite veritabanına kaydeder."""
    if not tum_ilanlar:
        print("Kaydedilecek veri bulunamadı!")
        return
        
    # DataFrame oluşturma
    df = pd.DataFrame(tum_ilanlar)
    
    # CSV kaydı
    df.to_excel("ilanlar.xlsx", index=False)
    print("Veriler başarıyla 'ilanlar.xlsx' dosyasına yazıldı.")
    
    # SQlite vertabanı kaydı
    try:
        baglanti = sqlite3.connect("ilanlarım.db")
        df.to_sql("ilanlar_tablosu", baglanti, if_exists="replace", index=False)
        baglanti.close()
        print("Veriler başarıyla 'iilanlarım.db' veritabanına işlendi.")
    except Exception as e:
        print(f"Veritabanı kayıt hatası: {e}") 
        
# --- Ana Çalıştırma Bloğu --- 
if __name__ == "__main__":  
    print("Web scraping operasyonu başlatılıyor...")
    ilan_listesi = ilanları_cek(50)
    disa_aktarma(ilan_listesi)
    print("Tüm işlemler başarıyla tamamlandı!")