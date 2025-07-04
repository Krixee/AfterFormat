# 🛠️ *AfterFormat* 🚀

**_Windows için güçlü ve kullanıcı dostu bir sistem kurulum ve optimizasyon aracı!_**  
*AfterFormat*, Windows format sonrası işlemleri kolaylaştırmak için tasarlanmış bir uygulamadır. 🎉 Popüler programları tek tıkla indirir, sistem sürücülerini tespit eder, gereksiz dosyaları temizler, DNS ayarlarını günceller ve Windows’u etkinleştirir. Tüm bu işlemler, *renkli ve sezgisel* bir arayüzle, **tek bir `.exe` dosyası** üzerinden yapılır! 😎  

---

## ✨ **Özellikler** ✨

- 📥 **Program İndirme**: *Spotify, Steam, Discord, WinRAR* gibi popüler uygulamaları otomatik indirir.  
- 🖥️ **Sürücü Tespiti**: *Anakart* ve *GPU* modelinizi tespit ederek doğru sürücü sayfalarına yönlendirir.  
- 🧹 **Sistem Temizleme**: Gereksiz dosyaları (*Temp, Recent, Prefetch, Çöp Kutusu* vb.) siler.  
- 🌐 **DNS Güncelleme**: DNS ayarlarını otomatik olarak *Cloudflare DNS*’e (`1.1.1.1`, `1.0.0.1`) günceller.  
- 🔑 **Windows Etkinleştirme**: Windows’u hızlıca etkinleştirir (*DİKKAT*: Third-party script kullanır, güvenilirliğini kontrol edin).  
- ⚠️ **Hata Yönetimi**: İndirme hatalarında diğer işlemlere devam eder, hataları sonunda raporlar.  
- 💾 **Tek Dosya Çözümü**: Tüm veriler (*programs.json* dahil) `main.py` içinde, ek dosya gerektirmez!  

---

## 🛠️ **Kurulum** 🛠️

1. **Gerekli Kütüphaneleri Yükleyin** 📦:  
   ```bash
   pip install requests beautifulsoup4 selenium webdriver-manager tqdm ttkthemes wmi pywin32
