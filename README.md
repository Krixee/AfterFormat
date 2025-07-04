# AfterFormat
Windows için program indirme, driver yükleme, sistem temizleme ve etkinleştirme aracı.

## Özellikler
- Program indirme (programs.json’dan).
- Anakart ve GPU driver’ları için yönlendirme.
- Gereksiz dosyaları temizleme.
- Windows etkinleştirme (DİKKAT: Third-party script kullanır, güvenilirliğini kontrol edin).

## Kurulum
1. `pip install requests beautifulsoup4 selenium webdriver-manager tqdm ttkthemes wmi pywin32`
2. `python main.py` veya `AfterFormat.exe`’yi yönetici olarak çalıştır.
3. `programs.json`’u aynı dizine koy.

## Uyarı
Windows etkinleştirme özelliği (`irm https://get.activated.win | iex`) third-party bir script kullanır. Kullanmadan önce riskleri değerlendirin.
