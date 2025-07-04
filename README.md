🛠️ AfterFormat 🚀
Windows için güçlü ve kullanıcı dostu bir sistem kurulum ve optimizasyon aracı!

AfterFormat, Windows format sonrası işlemleri kolaylaştırmak için tasarlanmıştır. 🎉

Popüler programları (Spotify, Steam, Discord, WinRAR vb.) tek tıkla indirir,
anakart ve GPU sürücülerini tespit eder,
gereksiz dosyaları temizler,
DNS ayarlarını Cloudflare DNS’e (1.1.1.1, 1.0.0.1) günceller
ve Windows’u etkinleştirir.

Renkli ve sezgisel arayüzü ile tüm işlemler tek bir .exe dosyası üzerinden yapılır! 😎

✨ Özellikler ✨
📥 Program İndirme: Spotify, Steam, Discord, WinRAR gibi uygulamaları otomatik indirir.

🖥️ Sürücü Tespiti: Anakart ve GPU modelinizi tespit edip doğru sürücü sayfalarına yönlendirir.

🧹 Sistem Temizleme: Temp, Recent, Prefetch, Çöp Kutusu gibi gereksiz dosyaları siler.

🌐 DNS Güncelleme: DNS ayarlarını Cloudflare DNS’e otomatik günceller.

🔑 Windows Etkinleştirme: Windows’u hızlıca etkinleştirir (DİKKAT: Third-party script kullanır, güvenilirliğini kontrol edin).

⚠️ Hata Yönetimi: İndirme hatalarında diğer işlemlere devam eder, hataları sonunda raporlar.

💾 Tek Dosya Çözümü: programs.json dahil tüm veriler main.py içinde, ek dosya gerektirmez!

🛠️ Kurulum 🛠️
Gerekli Kütüphaneleri Yükleyin 📦:
pip install requests beautifulsoup4 selenium webdriver-manager tqdm ttkthemes wmi pywin32

Programı Çalıştırın ▶️:
Kaynak kod için: python main.py
veya derlenmiş .exe için: AfterFormat.exe
(Not: Yönetici olarak çalıştırın!).

.exe Oluşturma (isteğe bağlı) 🔨:
cd C:\Users\***\Desktop\Afterformat && rmdir /s /q dist && pyinstaller --onefile --noconsole --name AfterFormat main.py
(Çıktı: dist/AfterFormat.exe)

⚠️ Uyarılar ⚠️
Windows Etkinleştirme:
irm https://get.activated.win | iex third-party script’i kullanılır.
Kullanmadan önce güvenilirliğini doğrulayın! 🔍

Yönetici İzni:
DNS ve etkinleştirme için yönetici izni gerekir.

Hata Kayıtları:
Sorunlarda error.log dosyasını kontrol edin. 📜

📚 Kullanım 📚
Programı yönetici olarak başlatın.

Programları ve işlemleri (DNS değiştirme, sürücü tespiti vb.) seçin. ✅

İndir’e tıklayın, renkli arayüzde ilerlemeyi izleyin! 🎨

Hatalı indirmeler atlanır, sonunda raporlanır. 🚫

🧑‍💻 Geliştirici 🧑‍💻
krixe tarafından geliştirildi. 💡
GitHub üzerinden sorularınızı veya önerilerinizi paylaşabilirsiniz! 📩
