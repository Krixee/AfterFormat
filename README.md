**🛠️ AfterFormat 🚀**
Windows için güçlü ve kullanıcı dostu bir sistem kurulum aracı!

AfterFormat, Windows format sonrası işlemleri kolaylaştırmak için tasarlanmıştır. 🎉

**✨ Özellikler ✨**
📥 Program İndirme: Spotify, Steam, Discord, WinRAR gibi uygulamaları otomatik indirir ve de bilgisayarınıza otomatik olarak kurar.

🖥️ Sürücü Tespiti: Anakart ve GPU modelinizi tespit edip doğru sürücü sayfalarına yönlendirir.

🧹 Sistem Temizleme: Temp, Recent, Prefetch, Çöp Kutusu gibi gereksiz dosyaları siler.

🌐 DNS Güncelleme: DNS ayarlarını(_IPV4 ve IPV6_) Cloudflare DNS(_1.1.1.1_)’e otomatik günceller.

🔑 Windows Etkinleştirme: Windows’u hızlıca etkinleştirir (_DİKKAT: Third-party script kullanır, güvenilirliğini kontrol edin_).

🪄 Windows Güncelleme: Windows'unuzun güncellemelerini denetler ve günceller. (_O esnada kurulan bir setup var ise güncelleme sonrası yeniden başlatmayı bekletir._)

⚠️ Hata Yönetimi: İndirme hatalarında diğer işlemlere devam eder, hataları sonunda raporlar.

**🛠️ Kurulum 🛠️**
Gerekli Kütüphaneleri Yükleyin 📦:
_pip install requests beautifulsoup4 selenium webdriver-manager tqdm ttkthemes wmi pywin32_

Programı Çalıştırın ▶️:
Kaynak kod için: python main.py
veya derlenmiş .exe için: AfterFormat.exe
(Not: Yönetici olarak çalıştırın!).

.exe Oluşturma (isteğe bağlı) 🔨:
cd C:\Users\***\Desktop\Afterformat && rmdir /s /q dist && pyinstaller --onefile --noconsole --name AfterFormat main.py
(Çıktı: dist/AfterFormat.exe)

**⚠️ Uyarılar ⚠️**
Windows Etkinleştirme:
irm https://get.activated.win | iex third-party script’i kullanılır.
Kullanmadan önce güvenilirliğini doğrulayın! 🔍

Yönetici İzni:
DNS ve etkinleştirme için yönetici izni gerekir.

Hata Kayıtları:
Sorunlarda error.log dosyasını kontrol edin. 📜

**📚 Kullanım 📚**
Programı yönetici olarak başlatın.

Programları ve işlemleri (DNS değiştirme, sürücü tespiti vb.) seçin. ✅

İndir’e tıklayın, arayüzde ilerlemeyi izleyin! 🎨

Hatalı indirmeler atlanır, sonunda raporlanır. 🚫

**🧑‍💻 Geliştirici 🧑‍💻**
krixe tarafından geliştirildi. 💡
GitHub üzerinden sorularınızı veya önerilerinizi paylaşabilirsiniz! 📩
