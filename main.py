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

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def log_error(message):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()}: {message}\n")

try:
    with open("programs.json", "r") as file:
        data = json.load(file)
        programs = data["programs"]
except Exception as e:
    log_error(f"programs.json yüklenemedi: {e}")
    programs = []

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

def download_file(url, filename, progress_label=None, status_label=None, popup=None):
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
                    status_label.config(text=f"↻ {downloaded_mb:.2f}/{total_size_mb:.2f} MB {filename}")
                    popup.update()
        log_error(f"{filename} indirildi!")
        if progress_label:
            progress_label.config(text=f"Tamamlandı: {filename}")
        if status_label and popup:
            status_label.config(text=f"✓ {downloaded_mb:.2f}/{total_size_mb:.2f} MB {filename}")
            popup.update()
        return filepath
    except Exception as e:
        log_error(f"Hata (download_file): {url} - {e}")
        if progress_label:
            progress_label.config(text=f"Hata: {filename} indirilemedi")
        if status_label and popup:
            status_label.config(text=f"✗ 0.00/{total_size_mb:.2f} MB {filename}")
            popup.update()
        return None

def start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, progress_label):
    selected_items = [(program, var) for program, var in selected_programs if var.get()]
    if not selected_items and not (motherboard_var.get() or gpu_var.get() or clean_var.get() or activate_var.get()):
        progress_label.config(text="Hiçbir program veya seçenek seçilmedi.")
        return

    popup = tk.Toplevel(root)
    popup.title("İndirme ve İşlem Durumu")
    popup.geometry("400x400")
    popup.configure(bg="#2e2e2e")

    status_labels = []
    for item, _ in selected_items:
        frame = ttk.Frame(popup)
        frame.pack(fill="x", padx=10, pady=5)
        status_label = ttk.Label(frame, text=f"↻ 0.00/0.00 MB {item['name']}", background="#2e2e2e", foreground="#ffffff")
        status_label.pack(anchor="w")
        status_labels.append(status_label)

    progress_label_popup = ttk.Label(popup, text="İşlemler başlatılıyor...", background="#2e2e2e", foreground="#ffffff")
    progress_label_popup.pack(pady=10)

    def download_thread():
        for (item, var), status_label in zip(selected_items, status_labels):
            name = item["name"]
            url = item["url"]
            direct_link = item["direct_link"]

            log_error(f"{name} için işlem başlatılıyor...")
            progress_label_popup.config(text=f"Hazırlanıyor: {name}")
            popup.update()

            if direct_link and check_link(direct_link):
                download_url = direct_link
            else:
                download_url = get_direct_link(url) or get_dynamic_link(url)

            if download_url:
                filename = f"{name.replace(' ', '_')}_setup.exe"
                download_file(download_url, filename, progress_label_popup, status_label, popup)
            else:
                log_error(f"{name} için indirme linki bulunamadı.")
                progress_label_popup.config(text=f"Hata: {name} için link bulunamadı")
                status_label.config(text=f"✗ 0.00/0.00 MB {name}")
                popup.update()

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

        status_message = "Tüm işlemler tamamlandı!"
        if clean_var.get():
            clean_temp_files()
            status_message += "\nGereksiz dosyalar temizlendi."
        if activate_var.get():
            progress_label_popup.config(text="Windows etkinleştiriliyor...")
            popup.update()
            if activate_windows():
                status_message += "\nWindows etkinleştirildi."
            else:
                status_message += "\nWindows etkinleştirme başarısız oldu."
                messagebox.showerror("Hata", "Windows etkinleştirme başarısız oldu. Detaylar için error.log dosyasını kontrol edin.")

        progress_label.config(text=status_message)
        progress_label_popup.config(text="Tüm işlemler tamamlandı!")
        popup.update()

    threading.Thread(target=download_thread).start()

def create_gui():
    root = ThemedTk(theme="equilux")
    root.title("AfterFormat")
    root.geometry("400x800")
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
    selected_drivers.append(("motherboard", motherboard_var))
    selected_drivers.append(("gpu", gpu_var))
    selected_drivers.append(("clean", clean_var))
    selected_drivers.append(("activate", activate_var))

    all_var = tk.BooleanVar()
    all_check = ttk.Checkbutton(root, text="Tümünü Seç", variable=all_var, command=lambda: [v.set(all_var.get()) for _, v in selected_programs + selected_drivers])
    all_check.pack(anchor="w", padx=30, pady=10)

    progress_label = ttk.Label(root, text="Durum: Hazır")
    progress_label.pack(pady=10)

    download_button = ttk.Button(root, text="İndir", command=lambda: start_download(root, selected_programs, motherboard_var, gpu_var, clean_var, activate_var, progress_label))
    download_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()