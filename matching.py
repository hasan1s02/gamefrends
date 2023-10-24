import threading
import socket
import time
import random
import mysql.connector
from enum import Enum
# Bağlantı bilgilerini tanımlayın
host = "0.0.0.0"  # Sunucu IP adresi
port = 12385  # Bağlantı portu


# Sunucu soketi oluşturun
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()



# Aktif oyuncuları saklamak için bir liste oluşturun
active_players = []
active_clients = []
active_clients_lock = threading.Lock()

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

# Eşleştirme işlevi
class MatchStatus(Enum):
    BEKLEMEDE = "Beklemede"
    KABUL = "Kabul"
    RED = "Red"

def add_to_active_clients(client_socket, username):
    with active_clients_lock:
        active_clients.append((client_socket, username))

def remove_from_active_clients(client_socket):
    with active_clients_lock:
        for entry in active_clients:
            if entry[0] == client_socket:
                active_clients.remove(entry)



def match_players(username,client_socket):
    # Kendi kullanıcı adınızı çıkarın

    while True:
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
        print(username)
        print("679238514")
        time.sleep(5)
        cursor_aktif.execute(
            "SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s AND kulllanici1_kabul = %s) OR (kullanici2 = %s AND kullanici2_kabul = %s) ORDER BY id DESC LIMIT 1",
            (username, MatchStatus.BEKLEMEDE.value, username, MatchStatus.BEKLEMEDE.value))
        match_control = cursor_aktif.fetchall()
        print("12341234fghdg54312")
        print(match_control)
        if match_control:

            if match_control[0][1] == username:
                match_friend = match_control[0][2]
            else:
                match_friend = match_control[0][1]
            send_message(username,match_friend)
            continue

        print("fghdg54312")
        cursor_aktif.execute("SELECT * FROM aktif_oyunlar4 WHERE kullanici_adi = %s", (username,))
        game_row = cursor_aktif.fetchall()

        if game_row:
            print(game_row)
            game_name = game_row[0][3]  # Oyun adını alın
        else:
            continue

        print("4325243645643")
        cursor_aktif.execute("SELECT kullanici_adi FROM aktif_oyunlar4 WHERE oyun_adi = %s", (game_name,))
        other_players = [row[0] for row in cursor_aktif.fetchall() if row[0] is not None]
        print("gdsdfghsfdg")
        if other_players:
            print(other_players)
            random_username = random.choice(other_players)
            print(f"Rastgele seçilen oyuncu: {random_username}")
        else:
            print("Başka oyuncu bulunamadı.")
        print(username)
        print(random_username)
        # Kendi ile eşleşmeyi önleme kontrolü
        if username == random_username:
            continue
        print("son")

        cursor_aktif.execute("SELECT * FROM eslesmeler2 WHERE ((kullanici1 = %s AND kullanici2 = %s) OR (kullanici2 = %s AND kullanici1 = %s))",(username, random_username, username, random_username))
        cevap = cursor_aktif.fetchall()
        if cevap:
            continue

        status_player1 = MatchStatus.BEKLEMEDE.value
        status_player2 = MatchStatus.BEKLEMEDE.value
        cursor_aktif.execute(
            "INSERT INTO eslesmeler2 (kullanici1, kullanici2, kulllanici1_kabul, kullanici2_kabul) VALUES (%s, %s, %s, %s)",
            (username, random_username, status_player1, status_player2))
        con_aktif.commit()
        send_message(username,random_username)
        time.sleep(10)



def send_message(username, message):
    print("send_message")
    print(username)
    print(message)
    status_player1 = MatchStatus.BEKLEMEDE.value
    status_player2 = MatchStatus.BEKLEMEDE.value

    with active_clients_lock:
        print("123412")
        print(active_clients)
        for client_socket, client_username in active_clients:
            print(client_socket)
            if client_username == username:
                print(client_username)
                client_socket.send(message.encode('utf-8'))




def add_friend():
    while True:
        time.sleep(100)
        try:
            con_aktif = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",
                database="aktif_oyunlar"
            )
            cursor_aktif = con_aktif.cursor()
        except mysql.connector.Error as err:
            print(f"Hata: {err}")

        query = "SELECT * FROM eslesmeler2 WHERE kulllanici1_kabul = 'kabul' AND kullanici2_kabul = 'kabul'"
        cursor_aktif.execute(query)

        accepted_matches = cursor_aktif.fetchall()
        print(accepted_matches)

        if accepted_matches:
            for match in accepted_matches:
                kullanici1 = match[1]
                kullanici2 = match[2]
                print("once")
                # Arkadaşlık durumunu kontrol et
                con_friend = mysql.connector.connect(
                    host="192.168.1.140",
                    user="root",
                    password="",
                    database="kullanici_bilgileri"
                )
                cursor_friend = con_friend.cursor()
                try:
                    check_friendship_query = "SELECT * FROM friend WHERE (username = %s AND username2 = %s) OR (username = %s AND username2 = %s)"
                    cursor_friend.execute(check_friendship_query, (kullanici1, kullanici2, kullanici1, kullanici2))
                    existing_friendship = cursor_friend.fetchall()
                except Exception as e:
                    print("Sorgu çalıştırılırken hata oluştu:", e)

                print(existing_friendship)

                if len(existing_friendship) > 0:
                    print("Zaten arkadaşsınız.")

                else:
                    print("dfsggsdfgsg234")
                    # Arkadaşlığı veritabanına kaydet

                    try:
                        add_friend_query = "INSERT INTO friend(username, username2) VALUES (%s, %s)"
                        cursor_friend.execute(add_friend_query, (kullanici1, kullanici2))
                        con_friend.commit()

                        print("Arkadaş başarıyla eklendi.")
                    except Exception as e:
                        print("Hata:", e)




while True:
    # Bağlantıyı kabul et
    print("asdqwe123")
    client_socket, client_address = server_socket.accept()
    print(f"Yeni bağlantı alındı: {client_address}")
    print(client_socket)
    print("asdqwe12345")
    # İstemciden kullanıcı adını alın (örneğin, bu veriyi bir HTTP isteği ile alabilirsiniz)
    username = client_socket.recv(1024).decode('utf-8')
    print(username)
    print(client_socket)
    print(client_address)

    active_clients.append((client_socket, username))

    print(active_clients)

    print("asdqwe12367")

    # Kullanıcının eşleşmesini kontrol eden bir iş parçası başlatın
    threading.Thread(target=match_players, args=(username,client_socket)).start()
    threading.Thread(target=add_friend).start()



"""
def match_players(username, client_socket):
    print(f"{username} için eşleştirme başlıyor...")

    # Kendi kullanıcı adına denk gelen eşleşme durumunu kontrol et
    con_aktif = mysql.connector.connect(
        host="192.168.1.140",
        user="root",
        password="",
        database="aktif_oyunlar"
    )
    cursor_aktif = con_aktif.cursor()
    cursor_aktif.execute("SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s OR kullanici2 = %s) AND (kulllanici1_kabul = %s OR kullanici2_kabul = %s)",
                        (username, username, MatchStatus.BEKLEMEDE.value, MatchStatus.BEKLEMEDE.value))
    existing_match = cursor_aktif.fetchone()
    if existing_match:

        send_message(username, "Eşleşme bekleniyor...")
        con_aktif.close()
        return

    # Aktif oyuncuları al
    cursor_aktif.execute("SELECT * FROM aktif_oyunlar4")
    active_players = [row[1] for row in cursor_aktif.fetchall()]
    con_aktif.close()

    # Kendi kullanıcı adını listeden çıkar
    active_players.remove(username)

    if active_players:
        # Rastgele bir rakip seç
        random_username = random.choice(active_players)

        # Seçilen rakiple daha önce eşleşme kontrolü yap
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
        cursor_aktif = con_aktif.cursor()
        cursor_aktif.execute("SELECT * FROM eslesmeler2 WHERE ((kullanici1 = %s AND kullanici2 = %s) OR (kullanici2 = %s AND kullanici1 = %s)) AND (kulllanici1_kabul = %s OR kullanici2_kabul = %s)",
                            (username, random_username, random_username, username, MatchStatus.BEKLEMEDE.value, MatchStatus.BEKLEMEDE.value))
        existing_match = cursor_aktif.fetchone()

        if existing_match:
            # Eşleşme zaten varsa, tekrar başlat
            con_aktif.close()
            match_players(username, client_socket)
        else:
            # Yeni bir eşleşme oluştur
            status_player1 = MatchStatus.BEKLEMEDE.value
            status_player2 = MatchStatus.BEKLEMEDE.value
            cursor_aktif.execute(
                "INSERT INTO eslesmeler2 (kullanici1, kullanici2, kulllanici1_kabul, kullanici2_kabul) VALUES (%s, %s, %s, %s)",
                (username, random_username, status_player1, status_player2))
            con_aktif.commit()

            # Eşleşme bulundu mesajını gönder
            send_message(username, f"Eşleşme bulundu! Rakip: {random_username}")
            con_aktif.close()
    else:
        # Eşleşme bulunamadı, bekleme mesajını gönder
        send_message(username, "Eşleşme bekleniyor...")
"""

"""import threading
import socket
import time
import random
import mysql.connector
from enum import Enum
# Bağlantı bilgilerini tanımlayın
host = "0.0.0.0"  # Sunucu IP adresi
port = 12385  # Bağlantı portu
port2 = 12386

# Sunucu soketi oluşturun
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()

communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
communication_socket.bind((host, port2))
communication_socket.listen()

# Aktif oyuncuları saklamak için bir liste oluşturun
active_players = []
active_clients = []

# Eşleştirme işlevi
class MatchStatus(Enum):
    BEKLEMEDE = "Beklemede"
    KABUL = "Kabul"
    RED = "Red"
def match_players(username,client_socket):
    print("zsfdgsd22131")

    time.sleep(10)


    try:
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
        cursor_aktif = con_aktif.cursor()
    except mysql.connector.Error as err:
        print(f"Hata: {err}")

    cursor_aktif.execute("SELECT * FROM aktif_oyunlar4")
    active_players = [row[1] for row in cursor_aktif.fetchall()]
    print("asdgf234325")
    if active_players:
        print(active_players)
        random_username = random.choice(active_players)
    else:
        match_players(username, client_socket)
        print(1)
        return

    print(2)

    print(username)
    print(active_players)
    if random_username:
        query = f"SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s AND kullanici2 = %s) OR (kullanici2 = %s AND kullanici1 = %s) "
        cursor_aktif.execute(query, (username, random_username, random_username,username))
        active_player = cursor_aktif.fetchone()
        if active_player:
            match_players(username, client_socket)
        else:
            print(random_username)
            # Eşleşme bulundu, eşleşme sonucunu gönderin
            status_player1 = MatchStatus.BEKLEMEDE.value
            status_player2 = MatchStatus.BEKLEMEDE.value
            print("2341")
            cursor_aktif.execute(
                "INSERT INTO eslesmeler2 (kullanici1, kullanici2, kulllanici1_kabul, kullanici2_kabul) VALUES (%s, %s, %s, %s)",
                (username, random_username, status_player1, status_player2))
            con_aktif.commit()
            message = f"Eşleşme bulundu! Rakip: {random_username}"
            send_message(username, message)
            time.sleep(5)
            print(username,random_username)
            print("123432")
            threading.Thread(target=send_message, args=(username, message)).start()
            time.sleep(1)
            decide =client_socket.recv(1024).decode('utf-8')
            print(decide)
            print("karar altı")
            query = f"SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s AND kullanici2 = %s) OR (kullanici1 = %s AND kullanici2 = %s)"
            cursor_aktif.execute(query, (username, random_username, random_username, username))
            active_player = cursor_aktif.fetchone()
            if decide == "kabul":
                if active_player[1] == username:
                    query = "UPDATE eslesmeler2 SET kulllanici1_kabul = 'kabul' WHERE id = %s"
                else:
                    query = "UPDATE eslesmeler2 SET kullanici2_kabul = 'kabul' WHERE id = %s"

                cursor_aktif.execute(query, (active_player[0],))
                con_aktif.commit()

                match_players(username, client_socket)
            else:
                if active_player[1] == username:
                    query = "UPDATE eslesmeler2 SET kulllanici1_kabul = 'red' WHERE id = %s"
                else:
                    query = "UPDATE eslesmeler2 SET kullanici2_kabul = 'red' WHERE id = %s"
                cursor_aktif.execute(query, (active_player[0],))
                con_aktif.commit()
                match_players(username, client_socket)
    else:
        # Eşleşme bulunamadı, beklemeye devam edin
        message = "Eşleşme bekleniyor..."
        send_message(username, message)
        match_players(username, client_socket)
    print("543645")
# İstemciye mesaj gönderme işlevi

def send_message(username, message):
    print("53247098657234hjkfdgls")
    print(username)
    for client_socket, client_username in active_clients:
        print(client_socket)
        if client_username == username:
            client_socket.send(message.encode('utf-8'))




def add_friend():
    while True:
        time.sleep(10)
        try:
            con_aktif = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",
                database="aktif_oyunlar"
            )
            cursor_aktif = con_aktif.cursor()
        except mysql.connector.Error as err:
            print(f"Hata: {err}")

        query = "SELECT * FROM eslesmeler2 WHERE kulllanici1_kabul = 'kabul' AND kullanici2_kabul = 'kabul'"
        cursor_aktif.execute(query)

        accepted_matches = cursor_aktif.fetchall()
        print(accepted_matches)

        if accepted_matches:
            for match in accepted_matches:
                kullanici1 = match[1]
                kullanici2 = match[2]
                print("once")
                # Arkadaşlık durumunu kontrol et
                con_friend = mysql.connector.connect(
                    host="192.168.1.140",
                    user="root",
                    password="",
                    database="kullanici_bilgileri"
                )
                cursor_friend = con_friend.cursor()
                try:
                    check_friendship_query = "SELECT * FROM friend WHERE (username = %s AND username2 = %s) OR (username = %s AND username2 = %s)"
                    cursor_friend.execute(check_friendship_query, (kullanici1, kullanici2, kullanici1, kullanici2))
                    existing_friendship = cursor_friend.fetchall()
                except Exception as e:
                    print("Sorgu çalıştırılırken hata oluştu:", e)

                print(existing_friendship)

                if len(existing_friendship) > 0:
                    print("Zaten arkadaşsınız.")

                else:
                    print("dfsggsdfgsg234")
                    # Arkadaşlığı veritabanına kaydet

                    try:
                        add_friend_query = "INSERT INTO friend(username, username2) VALUES (%s, %s)"
                        cursor_friend.execute(add_friend_query, (kullanici1, kullanici2))
                        con_friend.commit()

                        print("Arkadaş başarıyla eklendi.")
                    except Exception as e:
                        print("Hata:", e)

# İstemci bağlantılarını kabul etmek için sonsuz bir döngü başlatın
while True:
    # Bağlantıyı kabul et
    print("asdqwe123")
    client_socket, client_address = server_socket.accept()
    print(f"Yeni bağlantı alındı: {client_address}")
    print(client_socket)
    print("asdqwe12345")
    # İstemciden kullanıcı adını alın (örneğin, bu veriyi bir HTTP isteği ile alabilirsiniz)
    username = client_socket.recv(1024).decode('utf-8')
    print(username)
    # Kullanıcıyı aktif oyuncu listesine ekleyin
    a = 0
    for existing_client_socket, existing_username in active_clients:
        a = 1
        if existing_username == username:
            active_clients.remove((existing_client_socket, existing_username))
            active_clients.append((client_socket, username))



    print(active_clients)
    if a == 0:
        active_clients.append((client_socket, username))

    print("asdqwe12367")
    # Kullanıcının eşleşmesini kontrol eden bir iş parçası başlatın
    threading.Thread(target=match_players, args=(username,client_socket)).start()
    threading.Thread(target=add_friend).start()"""






"""import threading
import time
import mysql.connector
from enum import Enum
import random

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

# Eğer dosya yoksa oluştur
def create_queue_file():
    with open("queue.txt", "w") as f:
        pass

# Sıraya oyuncu ekle
def add_to_queue(player):
    with open("queue.txt", "a") as f:
        f.write(player + "\n")

# Sıradaki oyuncuyu al
def get_next_from_queue():
    try:
        with open("queue.txt", "r") as f:
            lines = f.readlines()
            if lines:
                next_player = lines[0].strip()
                updated_queue = lines[1:]
                with open("queue.txt", "w") as f:
                    f.writelines(updated_queue)
                return next_player
            else:
                return None
    except FileNotFoundError:
        create_queue_file()
        return None
class MatchStatus(Enum):
    BEKLEMEDE = "Beklemede"
    KABUL = "Kabul"
    RED = "Red"
# Eşleştirme fonksiyonu
def match_players(player1, player2):
    # Eşleşme algoritmasını burada uygula
    print(f"Eşleşme: {player1} - {player2}")



    def save_match_result(player1, player2):
        con_aktif = mysql.connector.connect(
            host="192.168.1.140",
            user="root",
            password="",
            database="aktif_oyunlar"
        )
        cursor_aktif = con_aktif.cursor()

        status_player1 = MatchStatus.BEKLEMEDE.value
        status_player2 = MatchStatus.BEKLEMEDE.value
        print("2341")
        cursor_aktif.execute(
            "INSERT INTO eslesmeler2 (kullanici1, kullanici2, kulllanici1_kabul, kullanici2_kabul) VALUES (%s, %s, %s, %s)",
            (player1, player2, status_player1, status_player2))
        con_aktif.commit()
        print("Eşleşme sonucu kaydedildi.")
        print(123)

    save_match_result(player1,player2)


# Kullanıcı eşleştirme döngüsü
def matching_loop():
    while True:
        try:
            con_aktif = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",
                database="aktif_oyunlar"
            )
            cursor_aktif = con_aktif.cursor()

            cursor_aktif.execute("SELECT * FROM aktif_oyunlar4")
            active_players = [row[1] for row in cursor_aktif.fetchall()]


            con_friend = mysql.connector.connect(
                host="192.168.1.140",
                user="root",
                password="",
                database="kullanici_bilgileri"
            )
            cursor_friend = con_friend.cursor()

            query = "SELECT * FROM eslesmeler2 WHERE kulllanici1_kabul = 'kabul' AND kullanici2_kabul = 'kabul'"
            cursor_aktif.execute(query)
            accepted_matches = cursor_aktif.fetchall()
            print(accepted_matches)

            if accepted_matches:
                for match in accepted_matches:
                    kullanici1 = match[1]
                    kullanici2 = match[2]
                    print("once")
                    # Arkadaşlık durumunu kontrol et

                    try:
                        check_friendship_query = "SELECT * FROM friend WHERE (username = %s AND username2 = %s) OR (username = %s AND username2 = %s)"
                        cursor_friend.execute(check_friendship_query, (kullanici1, kullanici2, kullanici1, kullanici2))
                        existing_friendship = cursor_friend.fetchall()
                    except Exception as e:
                        print("Sorgu çalıştırılırken hata oluştu:", e)

                    print(existing_friendship)

                    if len(existing_friendship) > 0:
                        print("Zaten arkadaşsınız.")

                    else:
                        print("dfsggsdfgsg234")
                        # Arkadaşlığı veritabanına kaydet

                        try:
                            add_friend_query = "INSERT INTO friend(username, username2) VALUES (%s, %s)"
                            cursor_friend.execute(add_friend_query, (kullanici1, kullanici2))
                            con_friend.commit()

                            print("Arkadaş başarıyla eklendi.")
                        except Exception as e:
                            print("Hata:", e)


            print("123")
            if len(active_players) >= 2:
                random.shuffle(active_players)
                print("456")
                i = 0
                while i < len(active_players):
                    if i + 1 < len(active_players):
                        player1 = active_players[i]
                        player2 = active_players[i + 1]

                        # Kendisiyle eşleşmeyi önleme kontrolü
                        if player1 != player2:
                            # Eşleşme zaten var mı kontrolü
                            if not is_match_exists(player1, player2):
                                match_players(player1, player2)

                        i += 2  # Sonraki çifti denemek için i'yi 2 artır
                    else:
                        # Tek bir oyuncu kaldı, onu sıraya al
                        add_to_queue(active_players[i])
                        i += 1

            # Sıradaki oyuncuyu eşleştirme
            next_player = get_next_from_queue()
            if next_player:
                match_next_loop_player(next_player)

            cursor_aktif.close()  # Bağlantıyı kapat
            con_aktif.close()  # Bağlantıyı kapat

            time.sleep(6)  # 6 saniye boyunca beklet, ardından tekrar
        except Exception as e:
            print("Hata:", e)
            time.sleep(6)
            continue  # Hata durumunda döngünün başına dön
# Diğer fonksiyonlar ve kod parçalarınızı buraya ekleyin...




def match_next_loop_player(player):
    with open("next_loop_players.txt", "a") as f:
        f.write(player + "\n")


# Eşleşme kontrolü
def is_match_exists(player1, player2):
    con_aktif = mysql.connector.connect(
        host="192.168.1.140",
        user="root",
        password="",
        database="aktif_oyunlar"
    )
    cursor_aktif = con_aktif.cursor()
    cursor_aktif.execute("SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s AND kullanici2 = %s) OR (kullanici1 = %s AND kullanici2 = %s)", (player1, player2, player2, player1))
    match = cursor_aktif.fetchone()
    time.sleep(2)
    cursor_aktif.close()  # Bağlantıyı kapat
    con_aktif.close()  # Bağlantıyı kapat
    return match is not None

# Eşleştirme döngüsünü başlat
matching_thread = threading.Thread(target=matching_loop)
matching_thread.start()
"""


