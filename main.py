import json
import os
import shutil
import requests
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from ttkthemes import ThemedTk
import wmi
import pythoncom
import webbrowser
import ipaddress
import ctypes

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def log_error(message):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()}: {message}\n")

PROGRAMS_DATA = {
    "programs": [
        {
            "name": "Spotify",
            "url": "https://www.spotify.com/download/windows/",
            "direct_link": "https://download.scdn.co/SpotifySetup.exe"
        },
        {
            "name": "Steam",
            "url": "https://store.steampowered.com/about/",
            "direct_link": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe"
        },
        {
            "name": "Discord",
            "url": "https://discord.com/download",
            "direct_link": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64"
        },
        {
            "name": "Razer Synapse",
            "url": "https://www.razer.com/synapse",
            "direct_link": None
        },
        {
            "name": "WinRAR",
            "url": "https://www.win-rar.com/download.html",
            "direct_link": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-712tr.exe"
        },
        {
            "name": "Lightshot",
            "url": "https://app.prntscr.com/en/download.html",
            "direct_link": "https://app.prntscr.com/build/setup-lightshot.exe"
        },
        {
            "name": "Attack Shark X3 Pro Driver",
            "url": "https://attackshark.com/pages/driver-download?srsltid=AfmBOoqmsPnGdBBgeHb7wqZps_xq5hhb6sTtcX-yPbNGWp1vcLc-dNfy",
            "direct_link": "https://support.attackshark.com/attackshark/ATTACK_SHARK_X3_PRO/Attack_Shark_Setup.exe"
        },
        {
            "name": "Google Chrome",
            "url": "https://www.google.com/chrome/",
            "direct_link": "https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B22294F9B-07C7-60D9-E5F5-74E99DDB9103%7D%26lang%3Dtr%26browser%3D4%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-statsdef_1%26installdataindex%3Dempty/update2/installers/ChromeSetup.exe"
        },
        {
            "name": "Outplayed for Overwolf",
            "url": "https://www.overwolf.com/app/overwolf-outplayed",
            "direct_link": "https://download.overwolf.com/install/Download?Name=Outplayed&ExtensionId=cghphpbjeabdkomiphingnegihoigeggcfphdofo&Channel=web_dl_btn&utm_content=new-light"
        },
        {
            "name": "Valorant",
            "url": "https://playvalorant.com/tr-tr/download/",
            "direct_link": "https://valorant.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.live.ap.exe"
        },
        {
            "name": "League of Legends",
            "url": "https://www.leagueoflegends.com/tr-tr/download/",
            "direct_link": "https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.tr.exe"
        }
    ]
}
programs = PROGRAMS_DATA["programs"]

def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except Exception as e:
        log_error(f"Link kontrol hatası: {url} - {e}")
        return False

def get_direct_link(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".exe") or "download" in href.lower():
                return href
        return None
    except Exception as e:
        log_error(f"Hata (get_direct_link): {url} - {e}")
        return None

def get_dynamic_link(url):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download') or contains(text(), 'Install') or contains(@class, 'download')]"))
        )
        link = download_button.get_attribute("href")
        driver.quit()
        return link
    except Exception as e:
        log_error(f"Hata (get_dynamic_link): {url} - {e}")
        driver.quit()
        return None

def get_hardware_info():
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()
        motherboard = c.Win32_BaseBoard()[0]
        motherboard_info = {"manufacturer": motherboard.Manufacturer, "product": motherboard.Product}
        gpu = c.Win32_VideoController()[0]
        gpu_info = {"name": gpu.Name}
        pythoncom.CoUninitialize()
        return motherboard_info, gpu_info
    except Exception as e:
        log_error(f"Donanım bilgisi alınamadı: {e}")
        pythoncom.CoUninitialize()
        return None, None

def open_driver_urls(motherboard, gpu):
    if motherboard:
        manufacturer = motherboard["manufacturer"].lower()
        if "asus" in manufacturer:
            webbrowser.open("https://www.asus.com/tr/support/download-center/")
        elif "msi" in manufacturer:
            webbrowser.open("https://tr.msi.com/support/download/")
        elif "gigabyte" in manufacturer:
            webbrowser.open("https://www.gigabyte.com/tr/Support/Consumer/Download")
    if gpu:
        gpu_name = gpu["name"].lower()
        if "nvidia" in gpu_name:
            webbrowser.open("https://www.nvidia.com/tr-tr/drivers/")
        elif "amd" in gpu_name:
            webbrowser.open("https://www.amd.com/en/support/download/drivers.html")
        elif "intel" in gpu_name:
            webbrowser.open("https://www.intel.com/content/www/us/en/support/detect.html")

def clean_temp_files():
    paths = [
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Temp"),
        os.path.expandvars(r"%SystemRoot%\Recent"),
        os.path.expandvars(r"%SystemRoot%\Temp"),
        os.path.expandvars(r"%SystemRoot%\$RECYCLE.BIN"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Tmp"),
        os.path.expandvars(r"%SystemRoot%\Prefetch")
    ]
    for path in paths:
        try:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                        except Exception as e:
                            log_error(f"Dosya silme hatası: {os.path.join(root, name)} - {e}")
                    for name in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, name), ignore_errors=True)
                        except Exception as e:
                            log_error(f"Klasör silme hatası: {os.path.join(root, name)} - {e}")
        except Exception as e:
            log_error(f"Yol işleme hatası: {path} - {e}")

def activate_windows():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "irm https://get.activated.win | iex"],
            capture_output=True,
            text=True,
            check=True
        )
        log_error(f"Windows etkinleştirme başarılı: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Windows etkinleştirme hatası: {e.stderr}")
        return False
    except Exception as e:
        log_error(f"Windows etkinleştirme hatası: {e}")
        return False

def validate_ip(ip, is_ipv6=False):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if is_ipv6 and not isinstance(ip_obj, ipaddress.IPv6Address):
            log_error(f"Geçersiz IPv6 adresi: {ip}")
            return False
        if not is_ipv6 and not isinstance(ip_obj, ipaddress.IPv4Address):
            log_error(f"Geçersiz IPv4 adresi: {ip}")
            return False
        return True
    except ValueError as e:
        log_error(f"IP doğrulama hatası: {ip} - {e}")
        return False

def change_dns():
    ipv4_primary = "1.1.1.1"
    ipv4_secondary = "1.0.0.1"
    ipv6_primary = "2606:4700:4700::1111"
    ipv6_secondary = "2606:4700:4700::1001"
    try:
        subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True,
            text=True,
            check=True
        )
        log_error("DNS önbelleği temizlendi.")

        result = subprocess.run(
            ["powershell", "-Command", "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"],
            capture_output=True,
            text=True,
            check=True
        )
        adapters = result.stdout.strip().split("\n")
        if not adapters or adapters == [""]:
            log_error("Hiçbir aktif ağ adaptörü bulunamadı.")
            return False

        success = True
        for adapter in adapters:
            adapter = adapter.strip()
            if not adapter:
                continue

            try:
                if validate_ip(ipv4_primary, is_ipv6=False):
                    subprocess.run(
                        ["powershell", "-Command", f"Set-DnsClientServerAddress -InterfaceAlias '{adapter}' -ServerAddresses ('{ipv4_primary}')"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    log_error(f"{adapter} için IPv4 birincil DNS {ipv4_primary} olarak ayarlandı.")
                if validate_ip(ipv4_secondary, is_ipv6=False):
                    subprocess.run(
                        ["powershell", "-Command", f"Set-DnsClientServerAddress -InterfaceAlias '{adapter}' -ServerAddresses ('{ipv4_primary}', '{ipv4_secondary}')"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    log_error(f"{adapter} için IPv4 ikincil DNS {ipv4_secondary} olarak ayarlandı.")

                if validate_ip(ipv6_primary, is_ipv6=True):
                    subprocess.run(
                        ["powershell", "-Command", f"Set-DnsClientServerAddress -InterfaceAlias '{adapter}' -ServerAddresses ('{ipv6_primary}')"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    log_error(f"{adapter} için IPv6 birincil DNS {ipv6_primary} olarak ayarlandı.")
                if validate_ip(ipv6_secondary, is_ipv6=True):
                    subprocess.run(
                        ["powershell", "-Command", f"Set-DnsClientServerAddress -InterfaceAlias '{adapter}' -ServerAddresses ('{ipv6_primary}', '{ipv6_secondary}')"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    log_error(f"{adapter} için IPv6 ikincil DNS {ipv6_secondary} olarak ayarlandı.")
            except subprocess.CalledProcessError as e:
                log_error(f"DNS değiştirme hatası ({adapter}): {e.stderr}")
                success = False
            except Exception as e:
                log_error(f"DNS değiştirme hatası ({adapter}): {e}")
                success = False

        subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True,
            text=True,
            check=True
        )
        log_error("DNS önbelleği tekrar temizlendi.")
        return success
    except subprocess.CalledProcessError as e:
        log_error(f"Ağ adaptörlerini listeleme hatası: {e.stderr}")
        return False
    except Exception as e:
        log_error(f"DNS değiştirme hatası: {e}")
        return False

def download_file(url, filename, progress_label=None):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        total_size_mb = total_size / (1024 * 1024)
        filepath = os.path.join("downloads", filename)
        with open(filepath, "wb") as f, tqdm(
            desc=filename,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            disable=progress_label is not None
        ) as bar:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                bar.update(len(chunk))
                if progress_label and total_size > 0:
                    downloaded_mb = downloaded / (1024 * 1024)
                    progress_label.config(text=f"↻ {downloaded_mb:.2f}/{total_size_mb:.2f} MB {filename}")
                    progress_label.update()
        log_error(f"{filename} indirildi!")
        if progress_label:
            progress_label.config(text=f"Tamamlandı: {filename}")
            progress_label.update()
        return filepath
    except Exception as e:
        log_error(f"Hata (download_file): {url} - {e}")
        if progress_label:
            progress_label.config(text=f"Hata: {filename} indirilemedi")
            progress_label.update()
        return None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, dns_var, progress_label):
    selected_items = [(program, var) for program, var in selected_programs if var.get()]
    if not selected_items and not (motherboard_var.get() or gpu_var.get() or clean_var.get() or activate_var.get() or dns_var.get()):
        progress_label.config(text="Hiçbir program veya seçenek seçilmedi.")
        return

    def download_thread():
        failed_downloads = []
        for item, _ in selected_items:
            name = item["name"]
            url = item["url"]
            direct_link = item["direct_link"]

            log_error(f"{name} için işlem başlatılıyor...")
            progress_label.config(text=f"Hazırlanıyor: {name}")
            progress_label.update()

            if direct_link and check_link(direct_link):
                download_url = direct_link
            else:
                download_url = get_direct_link(url) or get_dynamic_link(url)

            if download_url:
                filename = f"{name.replace(' ', '_')}_setup.exe"
                result = download_file(download_url, filename, progress_label)
                if not result:
                    failed_downloads.append(name)
            else:
                log_error(f"{name} için indirme linki bulunamadı.")
                progress_label.config(text=f"Hata: {name} için link bulunamadı")
                progress_label.update()
                failed_downloads.append(name)

        motherboard_info, gpu_info = None, None
        if motherboard_var.get() or gpu_var.get():
            motherboard_info, gpu_info = get_hardware_info()
            open_driver_urls(motherboard_info, gpu_info)
            message = "Tespit edilen "
            if motherboard_info:
                message += f"{motherboard_info['manufacturer']} {motherboard_info['product']}"
            if gpu_info:
                if motherboard_info:
                    message += " ve "
                message += f"{gpu_info['name']}"
            message += " için ilgili web sitelerinden manuel indirme yapmanız tavsiye edilir."
            messagebox.showinfo("Manuel İndirme", message)

        status_message = "Tüm işlemler tamamlandı! - by krixe"
        if clean_var.get():
            clean_temp_files()
            status_message += "\nGereksiz dosyalar temizlendi."
        if activate_var.get():
            progress_label.config(text="Windows etkinleştiriliyor...")
            progress_label.update()
            if activate_windows():
                status_message += "\nWindows etkinleştirildi."
            else:
                status_message += "\nWindows etkinleştirme başarısız oldu."
                messagebox.showerror("Hata", "Windows etkinleştirme başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")
        if dns_var.get():
            progress_label.config(text="DNS ayarları değiştiriliyor...")
            progress_label.update()
            if change_dns():
                status_message += "\nDNS Değiştirildi."
            else:
                status_message += "\nDNS değiştirme başarısız oldu."
                messagebox.showerror("Hata", "DNS değiştirme başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")

        if failed_downloads:
            status_message += "\nHata: " + ", ".join(failed_downloads) + " indirilemedi."

        progress_label.config(text=status_message)

    threading.Thread(target=download_thread).start()

def create_gui():
    if not is_admin():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Hata", "Program yönetici olarak çalıştırılmalı!")
        root.destroy()
        return

    root = ThemedTk(theme="equilux")
    root.title("AfterFormat")
    root.geometry("400x900")
    root.configure(bg="#2e2e2e")

    style = ttk.Style()
    style.configure("TLabel", background="#2e2e2e", foreground="#ffffff", font=("Arial", 12))
    style.configure("TCheckbutton", background="#2e2e2e", foreground="#ffffff", font=("Arial", 10))
    style.configure("TButton", background="#4a4a4a", foreground="#ffffff", font=("Arial", 10, "bold"))
    style.map("TButton", background=[("active", "#6a6a6a")])

    header_frame = ttk.Frame(root)
    header_frame.pack(pady=20)
    header_label = ttk.Label(header_frame, text="🛠️ AfterFormat", font=("Arial", 18, "bold"), background="#2e2e2e", foreground="#00b7eb")
    header_label.pack()

    label = ttk.Label(root, text="İndirmek istediğiniz programları seçin:")
    label.pack(pady=10)

    selected_programs = []
    for program in programs:
        var = tk.BooleanVar()
        chk = ttk.Checkbutton(root, text=program["name"], variable=var)
        chk.pack(anchor="w", padx=30, pady=2)
        selected_programs.append((program, var))

    driver_label = ttk.Label(root, text="Driver ve Sistem Seçenekleri:")
    driver_label.pack(pady=10)

    selected_drivers = []
    motherboard_var = tk.BooleanVar()
    gpu_var = tk.BooleanVar()
    clean_var = tk.BooleanVar()
    activate_var = tk.BooleanVar()
    dns_var = tk.BooleanVar()

    def check_motherboard():
        if motherboard_var.get():
            motherboard_info, _ = get_hardware_info()
            if motherboard_info:
                if not messagebox.askyesno("Anakart Tespiti", f"Anakart modeliniz: {motherboard_info['manufacturer']} {motherboard_info['product']}\nİndirmeye devam etmek istiyor musunuz?"):
                    motherboard_var.set(False)
            else:
                log_error("Anakart bilgisi alınamadı.")
                messagebox.showerror("Hata", "Anakart bilgisi alınamadı.")
                motherboard_var.set(False)

    def check_gpu():
        if gpu_var.get():
            _, gpu_info = get_hardware_info()
            if gpu_info:
                if not messagebox.askyesno("GPU Tespiti", f"GPU modeliniz: {gpu_info['name']}\nİndirmeye devam etmek istiyor musunuz?"):
                    gpu_var.set(False)
            else:
                log_error("GPU bilgisi alınamadı.")
                messagebox.showerror("Hata", "GPU bilgisi alınamadı.")
                gpu_var.set(False)

    motherboard_chk = ttk.Checkbutton(root, text="Anakart Driver'ları (Chipset ve LAN)", variable=motherboard_var, command=check_motherboard)
    motherboard_chk.pack(anchor="w", padx=30, pady=2)
    gpu_chk = ttk.Checkbutton(root, text="Ekran Kartı Driver'ı", variable=gpu_var, command=check_gpu)
    gpu_chk.pack(anchor="w", padx=30, pady=2)
    clean_chk = ttk.Checkbutton(root, text="Gereksiz dosyaları ve çöp kutusunu temizle", variable=clean_var)
    clean_chk.pack(anchor="w", padx=30, pady=2)
    activate_chk = ttk.Checkbutton(root, text="Windows'u Etkinleştir", variable=activate_var)
    activate_chk.pack(anchor="w", padx=30, pady=2)
    dns_chk = ttk.Checkbutton(root, text="DNS Değiştir", variable=dns_var)
    dns_chk.pack(anchor="w", padx=30, pady=2)

    selected_drivers.append(("motherboard", motherboard_var))
    selected_drivers.append(("gpu", gpu_var))
    selected_drivers.append(("clean", clean_var))
    selected_drivers.append(("activate", activate_var))
    selected_drivers.append(("dns", dns_var))

    all_var = tk.BooleanVar()
    all_check = ttk.Checkbutton(root, text="Tümünü Seç", variable=all_var, command=lambda: [v.set(all_var.get()) for _, v in selected_programs + selected_drivers])
    all_check.pack(anchor="w", padx=30, pady=10)

    progress_label = ttk.Label(root, text="Durum: Hazır")
    progress_label.pack(pady=10)

    download_button = ttk.Button(root, text="İndir", command=lambda: start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, dns_var, progress_label))
    download_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()