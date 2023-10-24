import socket
import mysql.connector
from datetime import datetime, timedelta
import threading
import json
import time
# Sunucu ayarları
host = '0.0.0.0'  # Sunucu IP adresi
port_main = 12354  # Port numarası


server_socket_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_main.bind((host, port_main))
server_socket_main.listen(10)



print(f"Sunucu {host}:{port_main} üzerinde dinleniyor...")

# Kullanıcıların oynadığı oyunları takip etmek için bir veri yapısı oluştur
# Her kullanıcı için bir oyun listesi olacak şekilde düşünebilirsiniz
user_games = {}
clients = {}  # Bağlı istemci soketleri
user_sockets = {}

#kullanıcı çıkmışmı kontroü sağlamak
user_last_activity = {}

# Oyunları işlemek için bir fonksiyon
def handle_game_info(username, game_name, masa_num):
    # Bu fonksiyon, sunucu tarafında gelen oyun bilgilerini işler
    # Veritabanına ekleme veya güncelleme işlemleri burada yapılabilir
    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    cursor_aktif = con_aktif.cursor()
    cursor_aktif.execute("SELECT DISTINCT masa_numarasi FROM aktif_oyunlar4 ")

    current_time = time.time()
    user_last_activity[username] = current_time

    aktif_oyunlarin_mac = cursor_aktif.fetchall()
    print("dsfadgfsdg")
    print(aktif_oyunlarin_mac)
    print("123456435")
    print(masa_num)
    print(type(masa_num))

    if game_name != "None":
        if masa_num not in [item[0] for item in aktif_oyunlarin_mac]:
            print("aktif oyun ekleme")
            cursor_aktif.execute(
                "INSERT INTO aktif_oyunlar4(kullanici_adi, masa_numarasi, oyun_adi) VALUES(%s, %s, %s)",
                (username, masa_num, game_name))
            con_aktif.commit()
        else:
            cursor_aktif.execute(
                "UPDATE aktif_oyunlar4 SET oyun_adi = %s WHERE kullanici_adi = %s AND masa_numarasi = %s",
                (game_name, username, masa_num))
            con_aktif.commit()
    else:
        print("fdwsaasfd")
        cursor_aktif.execute(
            "DELETE FROM aktif_oyunlar4 WHERE kullanici_adi = %s AND masa_numarasi = %s",
            (username, masa_num))
        con_aktif.commit()

def broadcast(sender_username, message):
    print(user_sockets)
    for username, client_socket in user_sockets.items():
        print(sender_username)
        print(username)
        if username != sender_username:
            print("asdeqweqwefds")
            try:
                client_socket.send(message.encode('utf-8'))
                print(f"Message sent to {username}: {message}")  # Mesaj gönderildiğini görüntüle
            except:
                remove_client(username)
def add_user(username, user_socket):
    user_sockets[username] = user_socket

def remove_user(username):
    print("user_socketsremove")
    print(user_sockets)
    if username in user_sockets:
        del user_sockets[username]

def remove_client(username):
    print("clientremove")
    print(clients)
    if username in clients:
        client_socket = clients[username]
        client_socket.close()
        del clients[username]
        remove_user(username)

# Kullanıcı etkinliklerini kontrol eden thread
def check_user_activity():
    while True:
        current_time = time.time()

        for username, last_activity_time in user_last_activity.items():
            inactive_threshold = 300  # 5 dakika (300 saniye) olarak ayarlandı

            if current_time - last_activity_time >= inactive_threshold:
                # Kullanıcı belirli süre boyunca etkinlik göstermediğinde yapılacak işlemler
                print(f"{username} kullanıcısı belirli süre boyunca etkinlik göstermedi.")
                try:
                    con_aktif = mysql.connector.connect(
                        host="192.168.1.140",
                        user="root",
                        password="",
                        database="aktif_oyunlar"
                    )
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

                cursor_aktif = con_aktif.cursor()
                select_query = "SELECT masa_numarasi FROM aktif_kullanicilar WHERE kullanici_adi = %s ORDER BY id DESC LIMIT 1"
                cursor_aktif.execute(select_query, (username,))
                masa_numarasi = cursor_aktif.fetchall()

                cikis_user(username, masa_numarasi)

        time.sleep(300)  # Her 5 dakikada bir kontrol et
def login(username,password,mac,client_socket):
    print("sdfsdf")
    try:
        con_kb = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
            database="kullanici_bilgileri"
        )
        cursor_kb = con_kb.cursor()
    except Exception as e:
        print("Bir hata oluştu: " + str(e))

    sorgulama = "SELECT * FROM user_data3 WHERE username = %s AND password = %s"
    cursor_kb.execute(sorgulama, (username, password))
    user_data = cursor_kb.fetchall()
    masa_numarasi = 1
    if user_data:
        try:
            con_aktif = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",
                database="aktif_oyunlar"
            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        cursor_aktif = con_aktif.cursor()

        con_mac = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
            database="mac_adresleri"
        )
        cursor_mac = con_mac.cursor()

        # MAC adreslerini çekme
        macadres_masa = "SELECT * FROM mac_adres"
        cursor_mac.execute(macadres_masa)
        mac_adresleri = cursor_mac.fetchall()
        print(mac_adresleri)

        for i in mac_adresleri:
            if mac == i[1]:
                masa_numarasi = i[0]
                break

        giris_saati = datetime.now()
        insert_query = "INSERT INTO aktif_kullanicilar (kullanici_adi,masa_numarasi, giris_saati) VALUES (%s,%s, %s)"
        cursor_aktif.execute(insert_query, (username, masa_numarasi, giris_saati))
        con_aktif.commit()
        print("asd")
        masa_numarasi2 = str(masa_numarasi)
        client_socket.send(masa_numarasi2.encode('utf-8'))
        print("as12")
        cursor_aktif.close()
        con_aktif.close()

    else:
        client_socket.send("Hatalı giriş".encode('utf-8'))

    client_socket.close()


def message_client(client_socket, address, username):
    while True:
        try:
            print(client_socket)

            print(username)
            print("a")
            message = client_socket.recv(1024).decode('utf-8')
            print("bb")
            if not message:
                print("cxc")
                remove_client(username)
                break
            print(message)
            # Mesajı ":" karakterine göre ayır
            parts = message.split(":::")

            # Gönderen kişi, mesaj numarası ve mesaj içeriğini al
            sender = parts[0]
            message_number = parts[1]
            message_content = parts[2]
            try:
                con_kb = mysql.connector.connect(
                    host="192.168.1.140",
                    user="root",
                    password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
                    database="kullanici_bilgileri"
                )
                cursor_kb = con_kb.cursor()
            except Exception as e:
                print("Bir hata oluştu: " + str(e))
            insert_message_query = "INSERT INTO messages (sender_username, receiver_username, message_text) VALUES (%s, %s, %s)"
            data = (sender, message_content, message_number)
            cursor_kb.execute(insert_message_query, data)
            con_kb.commit()

            broadcast(username, message)  # Burada kullanıcı adını ve mesajı doğru sırayla iletiyoruz
            target_user, real_message = message.split(":", 1)

            if target_user in user_sockets:
                target_socket = user_sockets[target_user]
                target_socket.send(real_message.encode('utf-8'))
        except:
            remove_client(username)
            break

def delete_friend(username,friend_name):
    try:
        try:
            con_kb = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
                database="kullanici_bilgileri"
            )
            cursor_kb = con_kb.cursor()
        except Exception as e:
            print("Bir hata oluştu: " + str(e))

        # Veritabanından arkadaşı sil
        delete_friend_query = "DELETE FROM friend WHERE (username = %s AND username2 = %s) OR (username = %s AND username2 = %s)"
        data = (username, friend_name, friend_name, username)
        cursor_kb.execute(delete_friend_query, data)
        con_kb.commit()
        print("silindi")
    except mysql.connector.Error as err:
        print(f"Hata: {err}")

def cikis_user(username,masa_numarasi):
    cikis_saati = datetime.now()
    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    cursor_aktif = con_aktif.cursor()

    update_query = "UPDATE aktif_kullanicilar SET cikis_saati = %s WHERE masa_numarasi = %s AND cikis_saati IS NULL"
    cursor_aktif.execute(update_query, (cikis_saati, masa_numarasi))
    con_aktif.commit()
    cursor_aktif.execute(
        "DELETE FROM aktif_oyunlar4 WHERE kullanici_adi = %s ",
        (username,))
    con_aktif.commit()
# Kullanıcı bağlantılarını kabul etmek için bir fonksiyon

def active_my_game(username):
    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
    except mysql.connector.Error as err:
        print(f"Hata: {err}")
        return

    cursor_aktif = con_aktif.cursor()

    # Kullanıcının oynadığı oyunu sorgulayın
    query = "SELECT oyun_adi FROM aktif_oyunlar4 WHERE kullanici_adi = %s"
    cursor_aktif.execute(query, (username,))
    active_game = cursor_aktif.fetchone()

    sql = "SELECT oyun_adi, COUNT(*) FROM aktif_oyunlar4 GROUP BY oyun_adi"
    cursor_aktif.execute(sql)

    # Sonuçları alın
    oyunlar = cursor_aktif.fetchall()

    # Oyunları ve oynayan kişi sayısını yazdırın
    for oyun, oyuncu_sayisi in oyunlar:
        print(f"{oyun}: {oyuncu_sayisi} kişi oynuyor")
    data = {
        "active_game": active_game[0] if active_game else "oyun oynanmiyor",
        "oyunlar": oyunlar
    }

    # Veriyi JSON formatına dönüştürün ve gönderin
    data_json = json.dumps(data)

    client_socket.send(data_json.encode('utf-8'))
    print("clientsocket")
    print(client_socket)

def handle_client(client_socket):
    print("dsfsdf")
    data = client_socket.recv(1024).decode('utf-8')
    message_parts = data.split(',')  # Mesajı parçalara ayır
    print("123")
    """if len(message_parts) < 6:
        print("Geçersiz mesaj formatı.")
        return"""
    message_type = message_parts[0]

    if message_type == "giris":
        # Giriş işlemi
        print("suıdfghısd")
        print(message_parts[1])
        print(message_parts[2])
        print(message_parts[3])

        username =message_parts[1]
        password = message_parts[2]
        masa_numarasi = message_parts[3]
        print(username,password,masa_numarasi,client_socket)
        login(username,password,masa_numarasi,client_socket)


    elif message_type == "oyun":
        # Oyun bilgisi işlemi
        username = message_parts[1]
        game_name = message_parts[2]
        masa_numarasi = int(message_parts[3])
        print(f"{username} oyun bilgisi gönderdi.")
        handle_game_info(username, game_name, masa_numarasi)

    elif message_type == "mesaj":
        username = message_parts[1]

        clients[username] = client_socket  # Kullanıcı adı ve bağlantıyı eşleştir
        add_user(username, client_socket)  # Kullanıcıyı user_sockets sözlüğüne ekleyin
        print("f")
        client_thread = threading.Thread(target=message_client, args=(client_socket, client_address, username))
        client_thread.start()
    elif message_type == "delete_friend":
        username = message_parts[1]
        friend_name = message_parts[2]
        print(message_parts)
        print("delete_friend")
        delete_friend(username,friend_name)

    elif message_type == "cikis":
        username = message_parts[1]
        masa_numarasi = message_parts[2]

        cikis_user(username,masa_numarasi)
    elif message_type == "game_aktif":
        username = message_parts[1]
        active_my_game(username)
    else:
        print("Bilinmeyen mesaj türü.")
def check_online_status(friend_name):
    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )

        cursor_aktif = con_aktif.cursor()

        query = "SELECT cikis_saati FROM aktif_kullanicilar WHERE kullanici_adi = %s ORDER BY giris_saati DESC LIMIT 1"
        cursor_aktif.execute(query, (friend_name,))
        result = cursor_aktif.fetchone()

        if result and result[0] is None:
            return "Çevrimiçi"  # Kullanıcı çevrimiçi
        else:
            return "Çevrimdışı"  # Kullanıcı çevrimdışı
    except mysql.connector.Error as err:
        print(f"Hata: {err}")
        return "Bilinmiyor"  # Durum bilinmiyor veya hata oluştu

def get_game_info(friend_name):
    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )

        cursor_aktif = con_aktif.cursor()

        query = "SELECT oyun_adi FROM aktif_oyunlar4 WHERE kullanici_adi = %s"
        cursor_aktif.execute(query, (friend_name,))
        result = cursor_aktif.fetchone()

        if result:
            return result  # Kullanıcının oyun bilgileri
        else:
            return "Oyun Oynamıyor"
    except mysql.connector.Error as err:
        print(f"Hata: {err}")
        return "Bilinmiyor"  # Bilgileri alamadı veya hata oluştu

def get_message_history(sender_username, receiver_username):
    con_kb = mysql.connector.connect(
        host="192.168.1.140",
        user="root",
        password="",  # Bu bilgiyi güvenli bir şekilde sakladığınızdan emin olun.
        database="kullanici_bilgileri"
    )

    cursor_kb = con_kb.cursor()

    # Veritabanından mesaj geçmişini çekmek için bir sorgu oluşturun ve verileri alın
    get_messages_query = "SELECT * FROM messages WHERE (sender_username = %s AND receiver_username = %s) OR (sender_username = %s AND receiver_username = %s) ORDER BY timestamp"
    data = (sender_username, receiver_username, receiver_username, sender_username)
    cursor_kb.execute(get_messages_query, data)
    messages = cursor_kb.fetchall()

    return messages

def start_message_server():
    # Sunucu ayarları
    # Özel mesajlaşma sunucu ayarları
    host2 = '0.0.0.0'
    port_message = 12355  # Özel mesajlaşma sunucu port numarası
    server_socket_message = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_message.bind((host2, port_message))
    server_socket_message.listen()

    print(f"Sunucu {host2}:{port_message} üzerinde dinleniyor...")

    while True:
        print("b")
        client_socket, client_address = server_socket_message.accept()
        print("c")
        username2 = client_socket.recv(1024).decode('utf-8')
        username3 = username2.split(',')
        username = username3[0]
        friend_name = username3[1]

        situation = check_online_status(friend_name)
        print(situation)
        game = get_game_info(friend_name)
        print(game)
        game_text = ",".join(game)
        messages = get_message_history(username,friend_name)
          # Tüm mesajları içeren bir liste (örnek olarak)
        message_list = []
        print(messages)
        for message in messages:
            sender = message[1]
            message_text = message[3]
            message_list.append(f"{sender}: {message_text}")
        message_string = "\n".join(message_list)
        # Verileri birleştirin ve JSON formatına çevirin

        data = {
            "situation": situation,
            "game_text": game_text,
            "message_string": message_string
        }

        message_json = json.dumps(data)

        # JSON verisini gönderin
        client_socket.send(message_json.encode('utf-8'))

        print("d")
        clients[username] = client_socket  # Kullanıcı adı ve bağlantıyı eşleştir
        add_user(username, client_socket)  # Kullanıcıyı user_sockets sözlüğüne ekleyin
        print("f")

        client_thread = threading.Thread(target=message_client, args=(client_socket, client_address, username))
        client_thread.start()

threading.Thread(target=start_message_server).start()


threading.Thread(target=check_user_activity).start()

while True:
    print("dinmliyorr")
    client_socket, client_address = server_socket_main.accept()
    print(f"{client_address} bağlandı.")
    print("dinmliyorr22")
    threading.Thread(target=handle_client, args=(client_socket,)).start()

