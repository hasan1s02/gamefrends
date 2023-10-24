import threading
import socket
import time
import mysql.connector

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
def decide(message_type,username,random_username):
    print("decideici")

    print(username)
    print(random_username)
    query = f"SELECT * FROM eslesmeler2 WHERE (kullanici1 = %s AND kullanici2 = %s) OR (kullanici1 = %s AND kullanici2 = %s)"
    cursor_aktif.execute(query, (username, random_username, random_username, username))
    active_player = cursor_aktif.fetchone()
    print("12376986532kjflfdghs")
    print(active_player)
    time.sleep(2)
    if message_type == "kabul":
        if active_player[1] == username:
            query = "UPDATE eslesmeler2 SET kulllanici1_kabul = 'kabul' WHERE id = %s"
        else:
            query = "UPDATE eslesmeler2 SET kullanici2_kabul = 'kabul' WHERE id = %s"

        cursor_aktif.execute(query, (active_player[0],))
        con_aktif.commit()


    else:
        if active_player[1] == username:
            query = "UPDATE eslesmeler2 SET kulllanici1_kabul = 'red' WHERE id = %s"
        else:
            query = "UPDATE eslesmeler2 SET kullanici2_kabul = 'red' WHERE id = %s"
        cursor_aktif.execute(query, (active_player[0],))
        con_aktif.commit()

    print("decidesonu")





while True:
    port2 = 12386
    host2 = "0.0.0.0"
    communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    communication_socket.bind((host2, port2))
    communication_socket.listen()

    print("Bağlantı bekleniyor...")
    client_socket, client_address = communication_socket.accept()
    print(f"Yeni bağlantı alındı: {client_address}")

    username = client_socket.recv(1024).decode('utf-8')

    message_parts = username.split(',')  # Mesajı parçalara ayır

    message_type = message_parts[0]
    username2 = message_parts[1]
    random_username = message_parts[2]

    print(f"{username2} sunucuya katıldı.")

    threading.Thread(target=decide, args=(message_type, username2, random_username)).start()






