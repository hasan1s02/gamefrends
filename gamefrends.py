import tkinter as tk
from tkinter import messagebox
import mysql.connector
from tkinter import scrolledtext, Entry, Button
from datetime import datetime, timedelta
from tkinter import ttk
import sys
import threading
import time
import uuid
import psutil
import socket
import json

mac_address = uuid.getnode()
mac_address_hex = '-'.join(['{:02x}'.format((mac_address >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])

masa_numarasi = 1


class BackgroundTask(threading.Thread):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.running = False
        self.start_time = None
        self.masa_numarasi = str(masa_numarasi)

    def run(self):
        self.running = True
        self.start_time = datetime.now()

        while self.running:
            current_time = datetime.now()
            elapsed_time = current_time - self.start_time

            server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası

            def send_game_info(username, game_name, masanum):
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(server_address)
                oyun = "oyun"
                dat2 = [oyun, username, game_name, masanum]

                dat = ','.join(dat2)
                # Kullanıcı adı ve şifreyi sunucuya gönder
                client_socket.send(dat.encode('utf-8'))

                client_socket.close()

            # Oyunların işlem adlarının bir listesi (örnek olarak)
            oyun_listesi = ["csgo.exe", "MinecraftLauncher.exe", "LeagueClient.exe", "VALORANT.exe", "zula.exe",
                            "hl.exe",
                            "FortniteLauncher.exe", "Wolfteam.bin", "dota2.exe", "r5apex.exe", "ExecPubg.exe",
                            "GTA5.exe",
                            "aces.exe", "FarCry5.exe", "StarCraft.exe", "eurotrucks2.exe", "Blur.exe", "GTAIV.exe",
                            "payday2_win32_release.exe", "left4dead2.exe", "Overwatch.exe", "KnightOnline.exe",
                            "Generals.exe",
                            "bf1.exe", "bfv.exe", "ModernWarfare.exe", "EMPIRES2.exe", "PointBlank.exe "]

            if elapsed_time >= timedelta(seconds=25):
                print("1 dakika geçti. Veritabanına kaydedebilirsiniz." + self.username)
                self.start_time = current_time

                aktif_surecler = {p.info['name']: p for p in psutil.process_iter(['pid', 'name'])}

                a = 1

                for oyun in oyun_listesi:
                    if oyun in aktif_surecler:
                        # Sunucuya oyun bilgisini gönder

                        send_game_info(self.username, oyun, self.masa_numarasi)
                        a = 0
                if a == 1:
                    send_game_info(self.username, "None", self.masa_numarasi)

            time.sleep(10)  # Her 20 saniyede bir kontrol et

    def stop(self):
        self.running = False


task_thread = None


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Giriş Yap")
        self.geometry("550x500")
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", padding=5, font=("Helvetica", 10))  # Özel düğme stili

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_ui()

    def init_ui(self):
        self.username_label = ttk.Label(self, text="Kullanıcı Adı:")
        self.username_input = ttk.Entry(self)

        self.password_label = ttk.Label(self, text="Şifre:")
        self.password_input = ttk.Entry(self, show="*")

        self.login_button = ttk.Button(self, text="Giriş Yap", style="Custom.TButton", command=self.login)
        self.register_button = ttk.Button(self, text="Kayıt Ol", style="Custom.TButton",
                                          command=self.open_register_window)

        self.username_label.pack(pady=5)
        self.username_input.pack(pady=5)

        self.password_label.pack(pady=5)
        self.password_input.pack(pady=5)

        self.login_button.pack(pady=10)
        self.register_button.pack()

        self.configure(bg="white")  # Arka plan rengini ayarlayın

    def login(self):
        username = self.username_input.get()
        password = self.password_input.get()

        # Sunucuya bağlan
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        masa_numarasi2 = str(masa_numarasi)
        giris = "giris"
        user_data = [giris, username, password, mac_address_hex]

        data = ','.join(user_data)
        # Kullanıcı adı ve şifreyi sunucuya gönder
        client_socket.send(data.encode('utf-8'))
        print("beklio")
        # Sunucudan gelen yanıtı al
        response = client_socket.recv(1024).decode('utf-8')
        print("defvvam")
        print(response)
        client_socket.close()

        if response == "Hatalı giriş":
            messagebox.showwarning("Hata", "Giriş başarısız. Kullanıcı adı veya şifre yanlış.")
        else:
            def start_task(username):
                global task_thread,masa_numarasi
                masa_numarasi = response
                if task_thread is None:
                    task_thread = BackgroundTask(username)
                    task_thread.start()

            start_task(username)
            self.open_blank_page(username)
    def on_closing(self):
        self.destroy()  # Pencereyi kapat
        sys.exit()

    def open_blank_page(self, username):
        self.withdraw()  # Ana pencereyi gizle
        self.blank_page = BlankPage(self, username)
        self.blank_page.deiconify()  # Boş sayfayı göster

    def open_register_window(self):
        self.withdraw()  # Pencereyi gizle
        self.register_window = RegisterWindow(self)
        self.register_window.deiconify()  # Pencereyi tekrar göster


class NewPage(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.username = username
        self.title("Eşleşme Sayfası")
        self.geometry("400x300")
        self.socket = None
        self.stop_thread = False
        self.kullanici_adi = None
        self.matched_user_name2 = None
        self.selected_answer = tk.StringVar()
        self.matched_user_name = tk.StringVar()
        self.question_text = tk.StringVar()
        self.matched_user_name.set("Eşleşme Bekleniyor")  # Başlangıçta "Eşleşme Bekleniyor" göster
        self.time_remaining = 30  # Başlangıçta kalan süreyi 30 saniye olarak ayarla
        self.time_label = tk.Label(self, text=f"Kalan Süre: {self.time_remaining} saniye", fg="blue")
        self.time_label.pack()
        self.timer_running = False  # Süre sayacı başlatılmadı
        # Soru ve seçenekleri göstermek için etiketleri ve düğmeleri ekleyin
        self.matched_user_label = tk.Label(self, textvariable=self.matched_user_name)
        self.matched_user_label.pack()

        self.question_label = tk.Label(self, textvariable=self.question_text)
        self.question_label.pack()
        self.iptal = 0
        self.sayac = 0
        self.option_a_button = tk.Button(self, text="A", command=lambda: self.select_answer("A"))
        self.option_a_button.pack(side="left", padx=10)
        self.option_b_button = tk.Button(self, text="B", command=lambda: self.select_answer("B"))
        self.option_b_button.pack(side="left", padx=10)
        self.option_c_button = tk.Button(self, text="C", command=lambda: self.select_answer("C"))
        self.option_c_button.pack(side="left", padx=10)
        self.option_d_button = tk.Button(self, text="D", command=lambda: self.select_answer("D"))
        self.option_d_button.pack(side="left", padx=10)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.send_button = tk.Button(self, text="Cevabı Gönder", command=self.send_answer)
        self.send_button.pack()
        self.send_button.config(state="disabled")
        self.feedback_label = tk.Label(self, text="", fg="green")  # Geri bildirim etiketi
        self.feedback_label.pack()
        self.return_button = Button(self, text="Boş Sayfaya Dön", command=self.return_to_blank)
        self.return_button.pack()
        self.client_socket_hizli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_hizli.connect(('192.168.1.157', 12395))

        self.client_socket_message = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_message.connect(('192.168.1.157', 12396))

        self.client_socket_message.send(self.username.encode('utf-8'))
        threading.Thread(target=self.receive_messages).start()
        self.worker_thread = threading.Thread(target=self.perform_some_action)
        self.worker_thread.start()
        # Mesaj gönderme için metin giriş alanı
        self.message_entry = tk.Entry(self)
        self.message_entry.pack()

        # Mesaj gönderme düğmesi
        self.send_message_button = tk.Button(self, text="Mesaj Gönder", command=self.send_message)
        self.send_message_button.pack()
        self.send_message_button.config(state="disabled")
        # Mesajları göstermek için bir metin alanı
        self.message_display = tk.Text(self)
        self.message_display.pack()



    def receive_messages(self):
        while True:
            try:
                print("bb")
                message = self.client_socket_message.recv(1024).decode('utf-8')
                print("cc")
                if not message:
                    print("Sunucuyla bağlantı kesildi.")
                    break
                print(message)  # Mesajları ekrana yazdırabilirsiniz

                parts = message.split(":::")
                if len(parts) == 3:
                    sender_username = parts[0]
                    message_text = parts[1]
                    receiver_username = parts[2]

                    # İşlem yapılabilir, örneğin sadece gönderen ve mesajı görüntüle
                    if receiver_username == self.username:
                        self.display_message(f"{sender_username}: {message_text}")

            except:
                print("Sunucuyla bağlantı kesildi.")
                break

    def display_message(self, message):
        self.message_display.insert(tk.END, f"{message}\n")

    def send_message(self):
        message = self.message_entry.get()
        if message and self.kullanici_adi:
            receiver_username = self.kullanici_adi
            print("fasfasr23w423")
            print(receiver_username)
            print(message)

            print(self.username)
            # Mesajı görüntüleme işlemleri
            self.display_message(f"{self.username}: {message}")
            self.message_entry.delete(0, tk.END)

            full_message = f"{self.username}:::{message}:::{receiver_username}"
            self.client_socket_message.send(full_message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def clear_page(self):
        # Tüm bileşenleri temizleyin
        self.matched_user_label.pack_forget()
        self.question_label.pack_forget()
        self.option_a_button.pack_forget()
        self.option_b_button.pack_forget()
        self.option_c_button.pack_forget()
        self.option_d_button.pack_forget()
        self.send_button.pack_forget()
        self.feedback_label.pack_forget()
        self.return_button.pack_forget()
        self.send_message_button.pack_forget()
        self.message_display.pack_forget()
        self.message_entry.pack_forget()
    def perform_some_action(self):
        username = self.username
        # Sunucuya katıldı bildirimi
        self.client_socket_hizli.send(username.encode('utf-8'))

        while True:
            # Eşleşme bildirimini bekleyin
            self.sayac += 1

            message = self.client_socket_hizli.recv(1024).decode('utf-8')
            if 20 < self.sayac:
                message = "stop"
            time.sleep(0.01)

            message_parts = message.split(":")
            message_type = message_parts[0]
            if message.startswith("Eşleşme oldu! İsim: "):
                self.send_message_button.config(state="normal")
                devam = "devam"
                self.client_socket_hizli.send(devam.encode('utf-8'))
                self.iptal = 1
                self.time_remaining = 30  # Süreyi sıfırla
                print("gelen mesaj")
                print(message)
                self.matched_user_name2 = message.split("İsim: ")[1]
                kullanici_adi = message.split(" İsim: ")[1].split(" Puanı:")[0]
                print("Kullanıcı Adı:", kullanici_adi)
                self.kullanici_adi = kullanici_adi
                self.matched_user_name.set(f"Eşleştiğiniz Kullanıcı: {self.matched_user_name2}")

                # Eşleşme olduğunda soruları ve şıkları gösterin
                print("12312312qwetrretwtwretwe5rt")

                time.sleep(10)
                self.start_timer()
                self.send_button.config(state="normal")
                sorular = self.client_socket_hizli.recv(1024).decode('utf-8')
                self.question_text.set(sorular)
            elif message_type == "SORU CEVAP":
                if message_parts[1] == "Ayni cevap!":
                    print("Aynı cevap verildi. Yeni soru gönderildi.")
                    feedback_text = "Aynı cevap verildi. Yeni soru gönderildi."
                    question21 = self.client_socket_hizli.recv(1024).decode('utf-8')
                    self.question_text.set(question21)
                    print("sdfaadfasd")
                    self.feedback_label.config(text=feedback_text, fg="green")
                    self.send_button.config(state="normal")
                elif message_parts[1] == "Farklı cevap!":
                    print("Farklı cevap gonderildi tekrar yanitlayin.")
                    feedback_text = "Farklı cevap gonderildi tekrar yanitlayin."
                    self.feedback_label.config(text=feedback_text, fg="red")
                    self.send_button.config(state="normal")
            elif message == "stop":
                break

    def start_timer(self):
        self.timer_running = True
        self.time_label.config(fg="blue")
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.time_remaining -= 1
            self.time_label.config(text=f"Kalan Süre: {self.time_remaining} saniye")
            if self.time_remaining <= 0:
                self.stop_timer()
                self.finish_match()
            else:

                self.time_label.after(1000, self.update_timer)  # Her 1 saniyede bir güncelle

    def stop_timer(self):
        self.timer_running = False
        self.time_label.config(fg="black")

    def select_answer(self, answer):
        self.selected_answer.set(answer)

        # Tüm düğmelerin rengini varsayılan olarak ayarla
        self.option_a_button.configure(bg="SystemButtonFace")
        self.option_b_button.configure(bg="SystemButtonFace")
        self.option_c_button.configure(bg="SystemButtonFace")
        self.option_d_button.configure(bg="SystemButtonFace")

        # Seçilen düğmeyi yeşil yap
        if answer == "A":
            self.option_a_button.configure(bg="green")

        elif answer == "B":
            self.option_b_button.configure(bg="green")
        elif answer == "C":
            self.option_c_button.configure(bg="green")
        elif answer == "D":
            self.option_d_button.configure(bg="green")

    def send_answer(self):
        answer = self.selected_answer.get()
        print(answer)
        if answer:
            print("fdghhgfddfg123123")
            self.client_socket_hizli.send(answer.encode('utf-8'))
            self.selected_answer.set("")  # Seçilen cevabı temizle
            self.send_button.config(state="disabled")
            # Tüm düğmelerin rengini varsayılan olarak ayarla
            self.option_a_button.configure(bg="SystemButtonFace")
            self.option_b_button.configure(bg="SystemButtonFace")
            self.option_c_button.configure(bg="SystemButtonFace")
            self.option_d_button.configure(bg="SystemButtonFace")
            feedback_text = "Arkadaşınızın cevabı bekleniyor."
            self.feedback_label.config(text=feedback_text, fg="red")

    def finish_match(self):
        # Sayfayı temizleyin
        def enable_buttons():
            button_accept.config(state=tk.DISABLED)
            button_reject.config(state=tk.DISABLED)
        print("assd")
        self.clear_page()
        print("ass123d")
        # JSON verisini alın
        self.client_socket_hizli.settimeout(14)
        received_data = self.client_socket_hizli.recv(1024).decode('utf-8')
        print("ass312312fdsad")
        # JSON verisini Python sözlüğüne dönüştürün
        received_dict = json.loads(received_data)

        # İlgili verileri alın
        dogru_cevap_sayisi = received_dict['dogru_cevap_sayisi']
        yanlis_cevap_sayisi = received_dict['yanlis_cevap_sayisi']
        farkli_cevap_sayisi = received_dict['farkli_cevap_sayisi']
        kazanilan_puan = received_dict['kazanilan_puan']
        eslesme_kisi = received_dict['eslesme_kisi']
        print("dfgsgfdsdfg")
        print(dogru_cevap_sayisi)
        # Yeni verileri göstermek için etiketler oluşturun
        dogru_label = tk.Label(self, text=f"Dogru Cevap Sayisi: {dogru_cevap_sayisi}")
        yanlis_label = tk.Label(self, text=f"Yanlis Cevap Sayisi: {yanlis_cevap_sayisi}")
        farkli_label = tk.Label(self, text=f"Farkli Cevap Sayisi: {farkli_cevap_sayisi}")
        kazanilan_puan_label = tk.Label(self, text=f"Kazanilan Puan: {kazanilan_puan}")
        eslesme_label = tk.Label(self, text=f"Eslesme Kisi: {eslesme_kisi}")

        # Etiketleri ekrana yerleştirin
        dogru_label.pack()
        yanlis_label.pack()
        farkli_label.pack()
        kazanilan_puan_label.pack()
        eslesme_label.pack()
        # İşlemi durdurmak için iki tuş ekleyin
        self.return_button = tk.Button(self, text="Anasayfaya Dön", command=self.return_to_blank)
        self.return_button.pack()

        self.find_match_button = tk.Button(self, text="Yeni Eşleşme Bul", command=self.return_to_blank_and_new_match)
        self.find_match_button.pack()

        button_accept = tk.Button(self, text="Kabul Et", command=lambda: button_click("accept"))
        button_accept.pack()

        button_reject = tk.Button(self, text="Reddet", command=lambda: button_click("reject"))
        button_reject.pack()
        self.after(15000, enable_buttons)

        def send_decision(decision):
            try:
                decision2 = decision
                print("decision değişkeni içeriği123:", decision)
                print("decision değişkeni içeriği:", decision2)
                data = f"{self.username},{decision2},{eslesme_kisi}"
                self.client_socket_hizli.send(data.encode('utf-8'))
                self.client_socket_hizli.close()
            except Exception as e:
                print("Sunucuya bağlanırken hata oluştu:", e)

        def button_click(decision):
            send_decision(decision)
            print("decision")
            print(decision)
            button_accept.config(state=tk.DISABLED)
            button_reject.config(state=tk.DISABLED)

    def return_to_blank(self):
        self.withdraw()  # Ana pencereyi gizle
        self.stop_timer()
        print(self.iptal)
        print("sadgfdrtw24e231")
        if self.iptal == 0:
            iptal = "iptal"
            self.client_socket_hizli.send(iptal.encode('utf-8'))
            print(self.iptal)
        self.blank_page = BlankPage(self, self.username)  # BlankPage'i oluştur
        self.blank_page.deiconify()

    def on_closing(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["cikis", self.username, masa_numarasi2]
        dat2 = ','.join(send_cikis)
        if self.iptal == 0:
            iptal = "iptal"
            self.client_socket_hizli.send(iptal.encode('utf-8'))
            print(self.iptal)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))

        self.withdraw()  # Ana pencereyi gizle
        self.blank = LoginWindow()  # BlankPage'i oluştur

        self.blank.deiconify()

        def stop_task():
            global task_thread
            if task_thread:
                task_thread.stop()
                task_thread.join()
                task_thread = None

        stop_task()
        self.destroy()  # Pencereyi kapat
        sys.exit()

    def return_to_blank_and_new_match(self):
        self.withdraw()  # Ana pencereyi gizle

        self.stop_timer()
        new_page = NewPage(self, self.username)  # Yeni sayfa sınıfını oluşturun
        new_page.mainloop()  # Yeni sayfayı görüntüleyin


class BlankPage(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.title("Boş Sayfa")
        self.geometry("550x500")

        self.username = username  # Kullanıcı adını saklayalım

        self.active_player = None
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.matched_player_text = tk.StringVar()
        self.matched_player_display = tk.Label(self, textvariable=self.matched_player_text)

        threading.Thread(target=self.match_time).start()

        self.delete_friend_entry = tk.Entry(self, width=30)
        self.delete_friend_entry.pack(padx=10, pady=10)
        self.delete_friend_button = tk.Button(self, text="Arkdaşalıktan Çıkar", command=self.delete_friend)
        self.delete_friend_button.pack(padx=10, pady=5)

        self.kendi_oyun_text = tk.StringVar()

        self.kendi_oyun_text.set("Oynadığınız Oyun: Oyun yok")

        self.games_info = {}
        self.oyun_bilgileri_label = tk.Label(self.main_frame)
        self.oyun_bilgileri_label.pack()

        self.label_style = {"font": ("Arial", 12)}
        self.show_active_game()

        self.update_interval = 5

        self.init_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.friend_listbox = tk.Listbox(self)
        self.friend_buttons = []  # Arkadaş tuşlarını tutacak liste
        self.show_friends()
        self.open_new_page_button = tk.Button(self.main_frame, text="Yeni Sayfa Aç", command=self.open_new_page)
        self.open_new_page_button.pack()

    def init_ui(self):

        # Kendi oynadığınız oyunu görüntülemek için bir etiket ekleyin
        self.kendi_oyun_label = tk.Label(self.main_frame, **self.label_style)
        self.kendi_oyun_label.pack()

        self.kendi_oyun_display = tk.Label(self.main_frame, textvariable=self.kendi_oyun_text)
        self.kendi_oyun_display.pack(side="top", anchor="nw")

        self.exit_button = Button(self.main_frame, text="Çıkış Yap", command=self.return_to_login)
        self.exit_button.pack()

        # Eşleşme durumu ve kabul/red etme seçeneklerini ekleyin
        self.match_status_label = tk.Label(self.main_frame, text="Eşleşme Durumu:")
        self.match_status_label.pack()
        self.match_status_text = tk.StringVar()
        self.match_status_display = tk.Label(self.main_frame, textvariable=self.match_status_text)
        self.match_status_display.pack()
        self.match_status_text.set("Sıradaki arkadaşınız aranıyor.")
        self.accept_button = tk.Button(self.main_frame, text="Kabul Et", command=self.accept_match)
        self.accept_button.pack()
        self.accept_button.config(state="disabled")  # Tuşu devre dışı bırak

        self.reject_button = tk.Button(self.main_frame, text="Red Et", command=self.reject_match)
        self.reject_button.pack()
        self.reject_button.config(state="disabled")  # Tuşu devre dışı bırak
        # Eşleşme geldiğinde eşleşen kişinin ismini gösteren bir etiket ekleyin
        self.matched_player_label = tk.Label(self.main_frame, text="Eşleşen Kişi:")
        self.matched_player_label.pack()
        self.matched_player_text = tk.StringVar()
        self.matched_player_display = tk.Label(self.main_frame, textvariable=self.matched_player_text)
        self.matched_player_display.pack()

        self.update_game_info()
        # Frame içindeki Canvas oluşturuluyor
        self.friends_canvas = tk.Canvas(self.main_frame)
        self.friends_canvas.pack(fill="both", expand=True)
        self.v_scrollbar = tk.Scrollbar(self.friends_canvas, orient="vertical", command=self.friends_canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.friends_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.friends_frame = tk.Frame(self.friends_canvas)
        self.friends_canvas.create_window((0, 0), window=self.friends_frame, anchor="nw")

    def open_new_page(self):
        # Yeni sayfayı açmak için bu işlevi kullanabilirsiniz
        self.withdraw()  # Boş sayfayı gizle
        new_page = NewPage(self, self.username)  # Yeni sayfa sınıfını oluşturun
        new_page.mainloop()  # Yeni sayfayı görüntüleyin

    def update_game_info(self):
        # Mevcut bilgileri temizle
        print("ghf")
        self.oyun_bilgileri_label.destroy()
        # Yeni bir etiket oluşturun
        self.oyun_bilgileri_label = tk.Label(self.main_frame)
        self.oyun_bilgileri_label.pack()
        game_info_str = "Oynanan Oyunlar:\n"
        for game, num_players in self.games_info.items():
            print(game)
            game_info_str += f"{game}: {num_players} kişi\n"

        self.oyun_bilgileri_label.config(text=game_info_str)

    def match_time(self):
        print("asdqwematrch")
        server_address = ('192.168.1.157', 12385)  # Sunucu adresi ve port numarası

        # Soketi oluşturun ve sunucuya bağlanın
        client_socket_match = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket_match.connect(server_address)
        client_socket_match.send(self.username.encode("utf-8"))

        while True:
            print("once")
            match_data = client_socket_match.recv(1024).decode('utf-8')
            print(match_data)

            self.matched_player_text.set(match_data + " ile eşleştiniz.")
            self.accept_button.config(state="normal")
            self.reject_button.config(state="normal")

    def delete_friend(self):

        friend_name = self.delete_friend_entry.get()
        print(friend_name)
        print(self.username)
        # Kullanıcının girdiği arkadaş adını al
        if friend_name:
            server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(server_address)
            send_delete_friend = ["delete_friend", self.username, friend_name]
            dat = ','.join(send_delete_friend)
            print(dat)
            client_socket.send(dat.encode('utf-8'))
        self.show_friends()

    def accept_match(self):
        matched_user = self.matched_player_text.get()
        # Metni "Rakip:" ifadesine göre bölelim
        # "Rakip:" kelimesinden sonrasını alalım
        opponent_username = matched_user.split("Rakip:", 1)[-1].strip().split()[0]
        print(opponent_username)

        if opponent_username:
            send_cikis2 = ["kabul", self.username, opponent_username]
            dat2 = ','.join(send_cikis2)

            server_address = ('192.168.1.157', 12386)  # Sunucu adresi ve port numarası

            # Soketi oluşturun ve sunucuya bağlanın
            client_socket_match2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket_match2.connect(server_address)
            client_socket_match2.send(dat2.encode("utf-8"))
            self.match_status_text.set("Sıradaki arkadaşınız aranıyor.")

            self.match_status_text.set("Eşleşme kabul edildi.")
            self.accept_button.config(state="disabled")  # Tuşu devre dışı bırak
            self.reject_button.config(state="disabled")  # Tuşu devre dışı bırak

    def reject_match(self):
        # Red işlemleri ve veritabanı güncellemesi burada yapılabilir
        self.match_status_text.set("Eşleşme reddedildi.")
        self.accept_button.config(state="disabled")  # Tuşu devre dışı bırak
        self.reject_button.config(state="disabled")  # Tuşu devre dışı bırak

    def show_active_game(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["game_aktif", self.username]
        dat2 = ','.join(send_cikis)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))
        time.sleep(0.1)
        received_data = client_socket.recv(1024).decode('utf-8')

        data = json.loads(received_data)
        active_game = data.get("active_game")
        print()
        oyun_oynayanlar = data.get("oyunlar")
        print(oyun_oynayanlar)
        print("sdfsdfsdf")
        self.games_info = {}
        for oyun, oyuncu_sayisi in oyun_oynayanlar:
            self.games_info[oyun] = oyuncu_sayisi

        self.update_game_info()

        if active_game == "oyun oynanmiyor":
            self.kendi_oyun_text.set("Oynadığınız Oyun: Oyun yok")

        else:
            oyun_adi = active_game
            self.kendi_oyun_text.set("Oynadığınız Oyun: " + oyun_adi)

        self.show_friends()

        self.after(20000, self.show_active_game)

    def on_closing(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["cikis", self.username, masa_numarasi2]
        dat2 = ','.join(send_cikis)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))

        self.withdraw()  # Ana pencereyi gizle
        self.blank = LoginWindow()  # BlankPage'i oluştur

        self.blank.deiconify()

        def stop_task():
            global task_thread
            if task_thread:
                task_thread.stop()
                task_thread.join()
                task_thread = None

        stop_task()
        self.destroy()  # Pencereyi kapat
        sys.exit()

    def open_main_window(self):
        self.withdraw()  # Boş sayfayı gizle
        self.main_window = MainWindow(self.username)  # Parent argümanını kaldırdık
        self.main_window.deiconify()  # Ana pencereyi tekrar göster

    def return_to_login(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["cikis", self.username, masa_numarasi2]
        dat2 = ','.join(send_cikis)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))

        self.withdraw()  # Ana pencereyi gizle
        self.blank = LoginWindow()  # BlankPage'i oluştur

        self.blank.deiconify()

        def stop_task():
            global task_thread
            if task_thread:
                task_thread.stop()
                task_thread.join()
                task_thread = None

        stop_task()

    def show_friends(self):
        try:
            # Mevcut arkadaş tuşlarını temizle
            for button in self.friend_buttons:
                button.destroy()
            self.friend_buttons = []  # Arkadaş tuşlarını saklayacak bir liste oluştur

            # Mevcut listeyi temizle ve çerçeveyi yok et
            if self.friend_listbox is not None:
                self.friend_listbox.destroy()
            self.friend_listbox = tk.Frame(self)  # Yeni bir arkadaş tuş çerçevesi oluştur
            self.friend_listbox.pack()

            # Mevcut canvas'ı temizle
            if self.friends_canvas is not None:
                self.friends_canvas.destroy()
                self.v_scrollbar.destroy()  # Dikey kaydırma çubuğunu da yok et
            self.friends_canvas = tk.Canvas(self.main_frame)  # Yeni bir canvas oluştur
            self.friends_canvas.pack(fill="both", expand=True)
            self.v_scrollbar = tk.Scrollbar(self.friends_canvas, orient="vertical", command=self.friends_canvas.yview)
            self.v_scrollbar.pack(side="right", fill="y")
            self.friends_canvas.configure(yscrollcommand=self.v_scrollbar.set)
            self.friends_frame = tk.Frame(self.friends_canvas)
            self.friends_canvas.create_window((0, 0), window=self.friends_frame, anchor="nw")

            con_kb = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
                database="kullanici_bilgileri"
            )

            cursor_kb = con_kb.cursor()

            # Kullanıcının arkadaşlarını veritabanından al
            get_friends_query = "SELECT CASE WHEN username = %s THEN username2 ELSE username END AS friend_username FROM friend WHERE username = %s OR username2 = %s"
            cursor_kb.execute(get_friends_query, (self.username, self.username, self.username))
            friend_usernames = cursor_kb.fetchall()

            y_position = 20
            for friend_username in friend_usernames:
                friend_button = tk.Button(self.friends_frame, text=friend_username[0],
                                          command=lambda name=friend_username[0]: self.send_message_to_friend(name))
                friend_button.pack(anchor="w", padx=10, pady=5)
                self.friend_buttons.append(friend_button)  # Oluşturulan arkadaş tuşunu listeye ekle
                y_position += 40

            # Canvas boyutunu ve kaydırma çubuklarını ayarla
            self.friends_canvas.update_idletasks()
            self.friends_canvas.config(scrollregion=self.friends_canvas.bbox("all"))

            self.friends_canvas.yview_moveto(0)  # Sayfayı en üstte başlatmak için

        except Exception as e:
            print("Bir hata oluştu: " + str(e))

    def open_add_friend_window(self):
        self.withdraw()  # Boş sayfayı gizle
        self.add_friend_window = AddFriendWindow(self, self.username)
        self.add_friend_window.deiconify()  # Arkadaş ekleme penceresini göster

    def send_message_to_friend(self, friend_name):
        self.withdraw()  # Boş sayfayı gizle
        self.main_window = MainWindow(self.username, friend_name)  # Parent argümanını kaldırdık
        self.main_window.deiconify()  # Ana pencereyi tekrar göster

        # Arkadaş adına ait mesaj geçmişini direkt olarak getir


class MainWindow(tk.Toplevel):
    def __init__(self, username, friend_name):
        super().__init__()

        self.username = username
        self.friend_name = friend_name
        self.title("Masaüstü Mesajlaşma Uygulaması")

        self.socket = None  # Bağlantıyı burada tanımlayın

        self.server_address = ('192.168.1.157', 12355)  # Sunucu adresi ve port

        self.connect_to_server()  # Pencere oluşturulurken otomatik olarak sunucuya bağlan

        self.send_button = Button(self, text="Gönder", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)
        # Enter tuşunu <Return> olayına bağla
        self.bind("<Return>", self.on_enter)
        self.return_button = Button(self, text="Boş Sayfaya Dön", command=self.return_to_blank)
        self.return_button.pack()

        self.message_history.see(tk.END)

    def on_enter(self, event):
        self.send_message()

    def connect_to_server(self):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.server_address)
                print("aa")
                a = [self.username, self.friend_name]
                dat = ','.join(a)
                self.socket.send(dat.encode('utf-8'))

                print("asdasfda")
                # JSON verisini alın
                received_data = self.socket.recv(1024).decode('utf-8')

                # JSON'u ayrıştırın
                data = json.loads(received_data)

                # Verileri alın
                situation = data.get("situation", "")
                game_text = data.get("game_text", "")
                message_string = data.get("message_string", "")
                print("asdasfda")
                self.user_activity_label = tk.Label(self, text=situation)
                self.user_activity_label.pack(padx=10, pady=5)

                self.game_info_label = tk.Label(self, text=game_text)
                self.game_info_label.pack(padx=10, pady=5)
                self.message_history = scrolledtext.ScrolledText(self, width=50, height=20)
                self.message_history.pack(padx=10, pady=10)
                print("asdasfda")
                print(game_text)
                self.message_history.delete(1.0, tk.END)

                print("sfdsqwexcv12")
                print(a)
                message_list = message_string.split('\n')
                for item in message_list:
                    parts = item.split(': ')
                    if len(parts) >= 2:
                        sender = parts[0]
                        message_text = ': '.join(parts[1:])
                        print(f"{sender}: {message_text}")
                        self.message_history.insert(tk.END, f"{sender}: {message_text}\n")
                    else:
                        print(item)

                self.message_entry = Entry(self, width=50)
                self.message_entry.pack(padx=10, pady=5)

                threading.Thread(target=self.receive_messages).start()
                print("sdfgdsgsfd12")
            except:
                print(f"Hata oluştu: {e}")

    def receive_messages(self):
        while True:
            try:
                print("bb")
                message = self.socket.recv(1024).decode('utf-8')
                print("cc")
                if not message:
                    print("Sunucuyla bağlantı kesildi.")
                    break
                print(message)  # Mesajları ekrana yazdırabilirsiniz

                parts = message.split(":::")
                if len(parts) == 3:
                    sender_username = parts[0]
                    message_text = parts[1]
                    receiver_username = parts[2]

                    # İşlem yapılabilir, örneğin sadece gönderen ve mesajı görüntüle
                    if receiver_username == self.username:
                        self.display_message(f"{sender_username}: {message_text}")

            except:
                print("Sunucuyla bağlantı kesildi.")
                break

    def send_message(self):
        message = self.message_entry.get()
        if message and self.friend_name:
            # İletilecek mesajı ve alıcıyı burada belirleyebilirsiniz
            receiver_username = self.friend_name

            print(message)
            print(self.friend_name)
            print(self.username)
            # Mesajı görüntüleme işlemleri
            self.display_message(f"{self.username}: {message}")
            self.message_entry.delete(0, tk.END)

            full_message = f"{self.username}:::{message}:::{self.friend_name}"
            self.socket.send(full_message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def on_closing(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["cikis", self.username, masa_numarasi2]
        dat2 = ','.join(send_cikis)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))

        self.withdraw()  # Ana pencereyi gizle
        self.blank = LoginWindow()  # BlankPage'i oluştur

        self.blank.deiconify()

        def stop_task():
            global task_thread
            if task_thread:
                task_thread.stop()
                task_thread.join()
                task_thread = None

        stop_task()
        self.destroy()  # Pencereyi kapat
        sys.exit()

    def display_message(self, message):
        self.message_history.insert(tk.END, f"{message}\n")
        self.message_history.see(tk.END)

    def return_to_blank(self):
        self.withdraw()  # Ana pencereyi gizle
        self.blank_page = BlankPage(self, self.username)  # BlankPage'i oluştur
        self.blank_page.deiconify()


class RegisterWindow(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Kayıt Formu")
        self.geometry("600x500")
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_ui()

    def init_ui(self):
        self.name_label = tk.Label(self, text="İsim:")
        self.name_input = tk.Entry(self)

        self.username_label = tk.Label(self, text="Kullanıcı Adı:")
        self.username_input = tk.Entry(self)

        self.email_label = tk.Label(self, text="Email:")
        self.email_input = tk.Entry(self)

        self.number_label = tk.Label(self, text="Telefon Numarası:")
        self.number_input = tk.Entry(self)

        self.gender_label = tk.Label(self, text="Cinsiyet:")
        self.gender_input = tk.StringVar(value="Erkek")
        self.gender_combobox = tk.OptionMenu(self, self.gender_input, "Erkek", "Kadın", "Diğer")

        self.country_label = tk.Label(self, text="Ülke:")
        self.country_input = tk.StringVar(value="Türkiye")
        self.country_combobox = tk.OptionMenu(self, self.country_input, "Türkiye", "ABD", "Hindistan", "Nepal",
                                              "Almanya")

        self.password_label = tk.Label(self, text="Şifre:")
        self.password_input = tk.Entry(self, show="*")

        self.age_label = tk.Label(self, text="Age:")
        self.age_input = tk.Entry(self)

        self.register_button = tk.Button(self, text="Kayıt Ol", command=self.register)
        self.return_button = tk.Button(self, text="Giriş Ekranına Dön", command=self.return_to_login)

        self.name_label.pack()
        self.name_input.pack()

        self.username_label.pack()
        self.username_input.pack()

        self.email_label.pack()
        self.email_input.pack()

        self.number_label.pack()
        self.number_input.pack()

        self.gender_label.pack()
        self.gender_combobox.pack()

        self.country_label.pack()
        self.country_combobox.pack()

        self.password_label.pack()
        self.password_input.pack()

        self.age_label.pack()
        self.age_input.pack()

        self.register_button.pack()
        self.return_button.pack()

    def on_closing(self):

        self.withdraw()  # Ana pencereyi gizle
        self.reg = LoginWindow()  # BlankPage'i oluştur

        self.reg.deiconify()

    def register(self):
        name = self.name_input.get()
        username = self.username_input.get()
        email = self.email_input.get()
        number = self.number_input.get()
        gender = self.gender_input.get()
        country = self.country_input.get()
        password = self.password_input.get()
        age = self.age_input.get()

        register_data = [name, username, email, number, gender, country, password, age]
        server_address = ('192.168.1.157', 12375)  # Sunucu adresi ve port numarası

        # Soketi oluşturun ve sunucuya bağlanın
        client_socket_register = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket_register.connect(server_address)

        register_data2 = ','.join(register_data)
        client_socket_register.send(register_data2.encode('utf-8'))

        time.sleep(0.1)
        data = client_socket_register.recv(1024).decode('utf-8')
        print(data)
        if data == "basarili":
            messagebox.showinfo("Başarılı", "Kayıt başarıyla tamamlandı.")
        elif data == "sifre":
            messagebox.showinfo("Hata", "Şifre en az 5 karakter olmalıdır.")
        elif data == "name":
            messagebox.showinfo("Geçersiz isim İsim en az 3 harf içermelidir ve sadece harf karakterleri içerebilir")
        elif data == "mail":
            messagebox.showinfo("Hata", "Geçersiz e-posta adresi. Lütfen geçerli bir e-posta adresi girin.")
        elif data == "number":
            messagebox.showinfo("Hata", "Geçersiz telefon numarası. Lütfen 11 haneli bir numara girin.")
        elif data == "number2":
            messagebox.showinfo("Hata", "Bu telefon numarası zaten kullanılıyor. Lütfen farklı bir numara girin.")
        elif data == "username":
            messagebox.showinfo("Hata", "Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.")

    def show_error_message(self, message):
        messagebox.showerror("Hata", message)

    def return_to_login(self):
        self.parent.deiconify()  # Ana pencereyi tekrar göster
        self.destroy()  # Pencereyi kapat


class AddFriendWindow(tk.Toplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.title("Arkadaş Ekle")
        self.geometry("500x400")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.init_ui()

    def init_ui(self):
        self.friend_label = tk.Label(self, text="Arkadaş Kullanıcı Adı:")
        self.friend_input = tk.Entry(self)

        self.add_button = tk.Button(self, text="Ekle", command=self.add_friend)
        self.return_button = tk.Button(self, text="Geri Dön", command=self.return_to_blank)

        self.friend_label.pack(padx=10, pady=10)
        self.friend_input.pack(padx=10, pady=5)
        self.add_button.pack(padx=10, pady=5)
        self.return_button.pack(padx=10, pady=10)

    def on_closing(self):
        server_address = ('192.168.1.157', 12354)  # Sunucu IP adresi ve port numarası
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)
        masa_numarasi2 = str(masa_numarasi)
        send_cikis = ["cikis", self.username, masa_numarasi2]
        dat2 = ','.join(send_cikis)
        print(dat2)
        client_socket.send(dat2.encode('utf-8'))

        self.withdraw()  # Ana pencereyi gizle
        self.blank = LoginWindow()  # BlankPage'i oluştur

        self.blank.deiconify()

        def stop_task():
            global task_thread
            if task_thread:
                task_thread.stop()
                task_thread.join()
                task_thread = None

        stop_task()

    def return_to_blank(self):
        self.parent.deiconify()  # Ana pencereyi tekrar göster
        self.parent.show_friends()
        self.destroy()  # Pencereyi kapat

    def add_friend(self):
        friend_username = self.friend_input.get()
        try:
            con_kb = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
                database="kullanici_bilgileri"
            )

            cursor_kb = con_kb.cursor()

            # Kullanıcının ID'sini bul
            get_user_query = "SELECT * FROM user_data3 WHERE username = %s"
            cursor_kb.execute(get_user_query, (self.username,))
            user_data = cursor_kb.fetchone()

            if user_data:
                user_id = user_data[2]

                # Arkadaşın ID'sini bul
                get_friend_query = "SELECT * FROM user_data3 WHERE username = %s"
                cursor_kb.execute(get_friend_query, (friend_username,))
                friend_data = cursor_kb.fetchone()

                if friend_data:
                    friend_id = friend_data[2]

                    # Arkadaşlık durumunu kontrol et
                    check_friendship_query = "SELECT * FROM friend WHERE (username = %s AND username2 = %s) OR (username = %s AND username2 = %s)"
                    cursor_kb.execute(check_friendship_query, (self.username, friend_id, friend_username, user_id))
                    existing_friendship = cursor_kb.fetchone()

                    if existing_friendship:
                        print("Zaten arkadaşsınız.")
                    else:
                        # Arkadaşlığı veritabanına kaydet
                        add_friend_query = "INSERT INTO friend(username, username2) VALUES (%s, %s)"
                        cursor_kb.execute(add_friend_query, (self.username, friend_id))
                        con_kb.commit()

                        print("Arkadaş başarıyla eklendi.")
                else:
                    print("Arkadaş kullanıcı adı bulunamadı.")
            else:
                print("Kullanıcı adı bulunamadı.")

        except Exception as e:
            print("Bir hata oluştu: " + str(e))


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

    message = MainWindow()
    message.mainloop()

    register = RegisterWindow()
    register.mainloop()

    blank = BlankPage()
    blank.mainloop()

    addfriend = AddFriendWindow()
    addfriend.mainloop()