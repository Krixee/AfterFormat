import json
import os
import shutil
import requests
import subprocess
import win32com.client
import pythoncom
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
import webbrowser
import ipaddress
import ctypes
import win32api
import win32con

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
            "direct_link": "https://download.scdn.co/SpotifySetup.exe",
            "install_args": "/silent"
        },
        {
            "name": "Steam",
            "url": "https://store.steampowered.com/about/",
            "direct_link": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe",
            "install_args": "/S"
        },
        {
            "name": "Discord",
            "url": "https://discord.com/download",
            "direct_link": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64",
            "install_args": "/S"
        },
        {
            "name": "Razer Synapse",
            "url": "https://www.razer.com/synapse",
            "direct_link": None,
            "install_args": "/S"
        },
        {
            "name": "WinRAR",
            "url": "https://www.win-rar.com/download.html",
            "direct_link": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-712tr.exe",
            "install_args": "/S"
        },
        {
            "name": "Lightshot",
            "url": "https://app.prntscr.com/en/download.html",
            "direct_link": "https://app.prntscr.com/build/setup-lightshot.exe",
            "install_args": "/S"
        },
        {
            "name": "Attack Shark X3 Pro Driver",
            "url": "https://attackshark.com/pages/driver-download?srsltid=AfmBOoqmsPnGdBBgeHb7wqZps_xq5hhb6sTtcX-yPbNGWp1vcLc-dNfy",
            "direct_link": "https://support.attackshark.com/attackshark/ATTACK_SHARK_X3_PRO/Attack_Shark_Setup.exe",
            "install_args": "/S"
        },
        {
            "name": "Google Chrome",
            "url": "https://www.google.com/chrome/",
            "direct_link": "https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B22294F9B-07C7-60D9-E5F5-74E99DDB9103%7D%26lang%3Dtr%26browser%3D4%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-statsdef_1%26installdataindex%3Dempty/update2/installers/ChromeSetup.exe",
            "install_args": "/silent /install"
        },
        {
            "name": "Outplayed for Overwolf",
            "url": "https://www.overwolf.com/app/overwolf-outplayed",
            "direct_link": "https://download.overwolf.com/install/Download?Name=Outplayed&ExtensionId=cghphpbjeabdkcomiphingnegihoigeggcfphdofo&Channel=web_dl_btn&utm_content=new-light",
            "install_args": "/S"
        },
        {
            "name": "Valorant",
            "url": "https://playvalorant.com/tr-tr/download/",
            "direct_link": "https://valorant.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.live.ap.exe",
            "install_args": "/S"
        },
        {
            "name": "League of Legends",
            "url": "https://www.leagueoflegends.com/tr-tr/download/",
            "direct_link": "https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.tr.exe",
            "install_args": "/S"
        }
    ]
}
programs = PROGRAMS_DATA["programs"]

def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except Exception as e:
        log_error(f"İnternet bağlantısı kontrol hatası: {e}")
        return False

def check_wuauserv():
    try:
        result = subprocess.run(
            ["sc", "query", "wuauserv"],
            capture_output=True,
            text=True,
            check=True
        )
        if "RUNNING" in result.stdout:
            return True
        else:
            subprocess.run(["net", "start", "wuauserv"], check=True)
            log_error("Windows Update servisi başlatıldı.")
            return True
    except subprocess.CalledProcessError as e:
        log_error(f"Windows Update servisi kontrol hatası: {e.stderr}")
        return False
    except Exception as e:
        log_error(f"Windows Update servisi kontrol hatası: {e}")
        return False

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

def check_and_install_windows_updates(progress_label, log_window=None):
    try:
        if not check_internet_connection():
            log_error("İnternet bağlantısı yok, Windows Update işlemi atlandı.")
            progress_label.config(text="Hata: İnternet bağlantısı yok, Windows Update atlandı.")
            if log_window:
                log_window.update_log("Hata: İnternet bağlantısı yok, Windows Update atlandı.", "error")
            return False, []

        if not check_wuauserv():
            log_error("Windows Update servisi çalışmıyor, işlem atlandı.")
            progress_label.config(text="Hata: Windows Update servisi çalışmıyor.")
            if log_window:
                log_window.update_log("Hata: Windows Update servisi çalışmıyor.", "error")
            return False, []

        pythoncom.CoInitialize()
        update_session = win32com.client.Dispatch("Microsoft.Update.Session")
        update_searcher = update_session.CreateUpdateSearcher()
        search_result = update_searcher.Search("IsInstalled=0")

        if search_result.Updates.Count == 0:
            log_error("Güncelleme bulunamadı.")
            progress_label.config(text="Windows güncellemeleri zaten güncel.")
            if log_window:
                log_window.update_log("Windows güncellemeleri zaten güncel.", "success")
            pythoncom.CoUninitialize()
            return True, []

        update_titles = [update.Title for update in search_result.Updates]
        progress_label.config(text=f"{search_result.Updates.Count} güncelleme bulundu, indiriliyor...")
        if log_window:
            log_window.update_log(f"{search_result.Updates.Count} güncelleme bulundu, indiriliyor...", "info")
        progress_label.update()

        downloader = update_session.CreateUpdateDownloader()
        downloader.Updates = search_result.Updates
        downloader.Download()

        installer = update_session.CreateUpdateInstaller()
        installer.Updates = search_result.Updates
        installer.Install()

        log_error(f"{search_result.Updates.Count} güncelleme kuruldu: {', '.join(update_titles)}")
        progress_label.config(text=f"{search_result.Updates.Count} güncelleme kuruldu.")
        if log_window:
            log_window.update_log(f"{search_result.Updates.Count} güncelleme kuruldu: {', '.join(update_titles)}", "success")
        pythoncom.CoUninitialize()
        return True, update_titles
    except win32com.client.pythoncom.com_error as e:
        log_error(f"Windows Update COM hatası: {e}")
        progress_label.config(text="Hata: Windows Update işlemi başarısız (COM hatası).")
        if log_window:
            log_window.update_log("Hata: Windows Update işlemi başarısız (COM hatası).", "error")
        pythoncom.CoUninitialize()
        return False, []
    except Exception as e:
        log_error(f"Windows Update hatası: {e}")
        progress_label.config(text="Hata: Windows Update işlemi başarısız.")
        if log_window:
            log_window.update_log("Hata: Windows Update işlemi başarısız.", "error")
        pythoncom.CoUninitialize()
        return False, []

def is_reboot_required():
    try:
        pythoncom.CoInitialize()
        update_session = win32com.client.Dispatch("Microsoft.Update.Session")
        update_searcher = update_session.CreateUpdateSearcher()
        search_result = update_searcher.Search("IsInstalled=0")
        reboot_needed = search_result.Updates.Count > 0

        if not reboot_needed:
            try:
                key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager", 0, win32con.KEY_READ)
                _, pending = win32api.RegQueryValueEx(key, "PendingFileRenameOperations")
                win32api.RegCloseKey(key)
                reboot_needed = bool(pending)
            except:
                pass

        pythoncom.CoUninitialize()
        return reboot_needed
    except Exception as e:
        log_error(f"Yeniden başlatma kontrol hatası: {e}")
        pythoncom.CoUninitialize()
        return False

def persist_after_reboot(state):
    try:
        script_path = os.path.abspath(__file__)
        task_name = "AfterFormatPostReboot"
        cmd = f'schtasks /create /tn "{task_name}" /tr "python \\"{script_path}\\"" /sc ONSTART /ru SYSTEM /f'
        subprocess.run(["powershell", "-Command", cmd], check=True)
        save_state(state)
        log_error("Yeniden başlatma sonrası görev oluşturuldu.")
    except Exception as e:
        log_error(f"Yeniden başlatma görevi oluşturma hatası: {e}")

def save_state(state):
    try:
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
        log_error("Durum kaydedildi: state.json")
    except Exception as e:
        log_error(f"Durum kaydetme hatası: {e}")

def load_state():
    try:
        if os.path.exists("state.json"):
            with open("state.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "dns_changed": False,
            "programs_installed": [],
            "drivers_checked": False,
            "temp_cleaned": False,
            "windows_activated": False,
            "windows_updated": False
        }
    except Exception as e:
        log_error(f"Durum yükleme hatası: {e}")
        return {
            "dns_changed": False,
            "programs_installed": [],
            "drivers_checked": False,
            "temp_cleaned": False,
            "windows_activated": False,
            "windows_updated": False
        }

def install_program(filepath, install_args, progress_label, log_window=None):
    try:
        if not os.path.exists(filepath):
            log_error(f"Kurulum dosyası bulunamadı: {filepath}")
            progress_label.config(text=f"Hata: {os.path.basename(filepath)} dosyası bulunamadı.")
            if log_window:
                log_window.update_log(f"Hata: {os.path.basename(filepath)} dosyası bulunamadı.", "error")
            return False
        if log_window:
            log_window.update_log(f"{os.path.basename(filepath)} kuruluyor.", "info")
        subprocess.run([filepath, install_args], check=True)
        log_error(f"{os.path.basename(filepath)} kuruldu.")
        progress_label.config(text=f"Tamamlandı: {os.path.basename(filepath)} kurulumu.")
        if log_window:
            log_window.update_log(f"{os.path.basename(filepath)} kurulumu tamamlandı.", "success", replace_last=True)
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Kurulum hatası: {filepath} - {e.stderr}")
        progress_label.config(text=f"Hata: {os.path.basename(filepath)} kurulumu başarısız.")
        if log_window:
            log_window.update_log(f"Hata: {os.path.basename(filepath)} kurulumu başarısız.", "error")
        return False
    except Exception as e:
        log_error(f"Kurulum hatası: {filepath} - {e}")
        progress_label.config(text=f"Hata: {os.path.basename(filepath)} kurulumu başarısız.")
        if log_window:
            log_window.update_log(f"Hata: {os.path.basename(filepath)} kurulumu başarısız.", "error")
        return False

def download_file(url, filename, progress_label=None, log_window=None):
    try:
        if log_window:
            log_window.update_log(f"{filename} indiriliyor.", "info")
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
        progress_label.config(text=f"Tamamlandı: {filename}")
        if log_window:
            log_window.update_log(f"{filename} indirildi.", "info")
        return filepath
    except Exception as e:
        log_error(f"Hata (download_file): {url} - {e}")
        progress_label.config(text=f"Hata: {filename} indirilemedi")
        if log_window:
            log_window.update_log(f"Hata: {filename} indirilemedi", "error")
        return None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class LogWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("AfterFormat İşlem Logları")
        self.window.geometry("700x500")
        self.window.configure(bg="#2e2e2e")
        self.window.transient(parent)
        self.window.grab_set()

        style = ttk.Style()
        style.configure("Log.TLabel", background="#2e2e2e", foreground="#00b7eb", font=("Arial", 14, "bold"))

        header_frame = ttk.Frame(self.window)
        header_frame.pack(pady=10, fill=tk.X)
        header_label = ttk.Label(header_frame, text="🛠️ İşlem Logları", style="Log.TLabel")
        header_label.pack()

        text_frame = ttk.Frame(self.window)
        text_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(text_frame, height=20, width=80, bg="#2e2e2e", fg="#ffffff", font=("Consolas", 11), wrap=tk.NONE)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(self.window, orient=tk.HORIZONTAL, command=self.text_area.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.config(xscrollcommand=h_scrollbar.set)

        self.text_area.tag_configure("success", foreground="#00ff00")
        self.text_area.tag_configure("error", foreground="#ff0000")
        self.text_area.tag_configure("info", foreground="#ffffff")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.last_program = None
        self.line_count = 0
        self.max_lines = 1000
        self.is_installing = False

    def update_log(self, message, tag="info", replace_last=False):
        if self.line_count >= self.max_lines:
            self.text_area.delete("1.0", "2.0")
            self.line_count -= 1

        timestamp = time.ctime()
        formatted_message = f"[{timestamp}] {message}"

        if replace_last and self.last_program:
            self.text_area.delete("end-2l", "end-1l")
            self.line_count -= 1

        self.text_area.insert(tk.END, formatted_message + "\n", tag)
        self.text_area.see(tk.END)
        self.window.update()
        self.line_count += 1
        self.last_program = message if "kurulumu tamamlandı" in message or "Hata" in message else None
        self.is_installing = message.endswith("kuruluyor.") and tag == "info"

    def on_closing(self):
        if messagebox.askokcancel("Kapat", "Log penceresini kapatmak istediğinizden emin misiniz?"):
            self.window.destroy()

def start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, dns_var, update_var, progress_label):
    selected_items = [(program, var) for program, var in selected_programs if var.get()]
    selected_options = sum([var.get() for _, var in selected_programs]) + sum([motherboard_var.get(), gpu_var.get(), clean_var.get(), activate_var.get(), dns_var.get(), update_var.get()])
    
    log_window = None
    if selected_options >= 2:
        log_window = LogWindow(root)

    state = load_state()

    def download_thread():
        failed_downloads = []
        installed_programs = state.get("programs_installed", [])

        if dns_var.get() and not state.get("dns_changed", False):
            progress_label.config(text="DNS ayarları değiştiriliyor...")
            if log_window:
                log_window.update_log("DNS ayarları değiştiriliyor...", "info")
            progress_label.update()
            if change_dns():
                state["dns_changed"] = True
                log_error("DNS değiştirme başarılı.")
                progress_label.config(text="DNS değiştirme başarılı.")
                if log_window:
                    log_window.update_log("DNS değiştirme başarılı.", "success")
            else:
                log_error("DNS değiştirme başarısız.")
                progress_label.config(text="Hata: DNS değiştirme başarısız.")
                if log_window:
                    log_window.update_log("Hata: DNS değiştirme başarısız.", "error")
                messagebox.showerror("Hata", "DNS değiştirme başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")
            save_state(state)

        for item, _ in selected_items:
            name = item["name"]
            if name in installed_programs:
                continue
            url = item["url"]
            direct_link = item["direct_link"]
            install_args = item.get("install_args", "/silent")

            log_error(f"{name} için işlem başlatılıyor...")
            progress_label.config(text=f"Hazırlanıyor: {name}")
            if log_window:
                log_window.update_log(f"{name} için işlem başlatılıyor...", "info")
            progress_label.update()

            if direct_link and check_link(direct_link):
                download_url = direct_link
            else:
                download_url = get_direct_link(url) or get_dynamic_link(url)

            if download_url:
                filename = f"{name.replace(' ', '_')}_setup.exe"
                result = download_file(download_url, filename, progress_label, log_window)
                if result:
                    progress_label.config(text=f"Kuruluyor: {name}")
                    if log_window:
                        log_window.update_log(f"{name} kuruluyor.", "info")
                    progress_label.update()
                    if install_program(result, install_args, progress_label, log_window):
                        installed_programs.append(name)
                        state["programs_installed"] = installed_programs
                        save_state(state)
                    else:
                        failed_downloads.append(name)
                else:
                    failed_downloads.append(name)
            else:
                log_error(f"{name} için indirme linki bulunamadı.")
                progress_label.config(text=f"Hata: {name} için link bulunamadı")
                if log_window:
                    log_window.update_log(f"Hata: {name} için link bulunamadı", "error")
                progress_label.update()
                failed_downloads.append(name)

        if (motherboard_var.get() or gpu_var.get()) and not state.get("drivers_checked", False):
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
            state["drivers_checked"] = True
            save_state(state)
            if log_window:
                log_window.update_log(message, "info")

        status_message = "Tüm işlemler tamamlandı! - by krixe"
        if clean_var.get() and not state.get("temp_cleaned", False):
            clean_temp_files()
            status_message += "\nGereksiz dosyalar temizlendi."
            state["temp_cleaned"] = True
            save_state(state)
            if log_window:
                log_window.update_log("Gereksiz dosyalar temizlendi.", "success")

        if activate_var.get() and not state.get("windows_activated", False):
            progress_label.config(text="Windows etkinleştiriliyor...")
            if log_window:
                log_window.update_log("Windows etkinleştiriliyor...", "info")
            progress_label.update()
            if activate_windows():
                status_message += "\nWindows etkinleştirildi."
                state["windows_activated"] = True
                save_state(state)
                if log_window:
                    log_window.update_log("Windows etkinleştirildi.", "success")
            else:
                status_message += "\nWindows etkinleştirme başarısız oldu."
                messagebox.showerror("Hata", "Windows etkinleştirme başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")
                if log_window:
                    log_window.update_log("Hata: Windows etkinleştirme başarısız oldu.", "error")

        if update_var.get() and not state.get("windows_updated", False):
            progress_label.config(text="Windows Update kontrol ediliyor...")
            if log_window:
                log_window.update_log("Windows Update kontrol ediliyor...", "info")
            progress_label.update()
            success, update_titles = check_and_install_windows_updates(progress_label, log_window)
            if success:
                status_message += f"\nWindows güncellemeleri tamamlandı: {', '.join(update_titles) if update_titles else 'Güncel'}"
                state["windows_updated"] = True
                save_state(state)
                if is_reboot_required():
                    max_wait_time = 300  # 5 dakika
                    wait_interval = 60   # 60 saniye
                    elapsed_time = 0
                    while log_window and log_window.is_installing and elapsed_time < max_wait_time:
                        progress_label.config(text="Kurulum devam ediyor, yeniden başlatma geciktiriliyor...")
                        if log_window:
                            log_window.update_log("Kurulum devam ediyor, yeniden başlatma geciktiriliyor...", "info")
                        time.sleep(wait_interval)
                        elapsed_time += wait_interval
                    persist_after_reboot(state)
                    status_message += "\nYeniden başlatma gerekiyor, sistem 30 saniye içinde yeniden başlatılacak."
                    messagebox.showinfo("Yeniden Başlatma", "Güncellemeler için sistem yeniden başlatılacak.")
                    if log_window:
                        log_window.update_log("Yeniden başlatma gerekiyor, sistem 30 saniye içinde yeniden başlatılacak.", "info")
                    subprocess.run(["shutdown", "/r", "/t", "30"])
            else:
                status_message += "\nWindows Update başarısız oldu."
                messagebox.showerror("Hata", "Windows Update başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")

        if failed_downloads:
            status_message += "\nHata: " + ", ".join(failed_downloads) + " indirilemedi veya kurulamadı."
        if installed_programs:
            status_message += "\nKurulan programlar: " + ", ".join(installed_programs)

        if not is_reboot_required() and os.path.exists("state.json"):
            subprocess.run(["powershell", "-Command", f"schtasks /delete /tn AfterFormatPostReboot /f"], capture_output=True)
            os.remove("state.json")
            log_error("Durum dosyası ve görev zamanlayıcı temizlendi.")
            if log_window:
                log_window.update_log("Durum dosyası ve görev zamanlayıcı temizlendi.", "info")

        progress_label.config(text=status_message)
        if log_window:
            log_window.update_log("Tüm işlemler tamamlandı!", "success")

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

    label = ttk.Label(root, text="İndirmek ve kurmak istediğiniz programları seçin:")
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
    update_var = tk.BooleanVar(value=True)

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

    def check_dns():
        if dns_var.get():
            messagebox.showinfo("DNS Değiştirme", "DNS ayarları Cloudflare DNS (1.1.1.1, 1.0.0.1) olarak güncellenecek. Bu, internet hızını ve güvenliğini artırabilir.")

    motherboard_chk = ttk.Checkbutton(root, text="Anakart Driver'ları (Chipset ve LAN)", variable=motherboard_var, command=check_motherboard)
    motherboard_chk.pack(anchor="w", padx=30, pady=2)
    gpu_chk = ttk.Checkbutton(root, text="Ekran Kartı Driver'ı", variable=gpu_var, command=check_gpu)
    gpu_chk.pack(anchor="w", padx=30, pady=2)
    clean_chk = ttk.Checkbutton(root, text="Gereksiz dosyaları ve çöp kutusunu temizle", variable=clean_var)
    clean_chk.pack(anchor="w", padx=30, pady=2)
    activate_chk = ttk.Checkbutton(root, text="Windows'u Etkinleştir", variable=activate_var)
    activate_chk.pack(anchor="w", padx=30, pady=2)
    dns_chk = ttk.Checkbutton(root, text="DNS Değiştir (Cloudflare)", variable=dns_var, command=check_dns)
    dns_chk.pack(anchor="w", padx=30, pady=2)
    update_chk = ttk.Checkbutton(root, text="Windows Güncellemelerini Yap", variable=update_var)
    update_chk.pack(anchor="w", padx=30, pady=2)

    selected_drivers.append(("motherboard", motherboard_var))
    selected_drivers.append(("gpu", gpu_var))
    selected_drivers.append(("clean", clean_var))
    selected_drivers.append(("activate", activate_var))
    selected_drivers.append(("dns", dns_var))
    selected_drivers.append(("update", update_var))

    all_var = tk.BooleanVar()
    all_check = ttk.Checkbutton(root, text="Tümünü Seç", variable=all_var, command=lambda: [v.set(all_var.get()) for _, v in selected_programs + selected_drivers])
    all_check.pack(anchor="w", padx=30, pady=10)

    progress_label = ttk.Label(root, text="Durum: Hazır")
    progress_label.pack(pady=10)

    download_button = ttk.Button(root, text="İndir ve Kur", command=lambda: start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, dns_var, update_var, progress_label))
    download_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()