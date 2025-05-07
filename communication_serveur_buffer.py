import socket
import json
import time
import sys
import select
from reception_serveur import recevoir_messages_jsonl

HOST = ''  # Listen on all available network interfaces
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"🟢 Serveur en écoute sur le port {PORT}")

    conn, addr = server_socket.accept()
    with conn:
        print("✅ Connecté par", addr)
        msg = conn.recv(1024)
        print("📥 Message reçu :",repr(msg))
        if msg == b"HELLO\n":
            conn.send(b"ACK\n")
            print("✅ Message de bienvenue envoyé au client ACK")
        else:
            print("❌ Message de bienvenue non reconnu, fermeture de la connexion.")
            conn.close()
            sys.exit(1)
        # Attente de 30 secondes avant d'envoyer la couleur
        print("⏳ Attente de 10 secondes avant d'envoyer la couleur...")
        time.sleep(10)

        couleur = "bleu"
        conn.sendall(json.dumps(couleur).encode())
        print("🎨 Couleur envoyée :", couleur)

        print("⏳ Attente de 15 secondes avant d'envoyer START_MATCH...")
        time.sleep(15)
        conn.sendall(b"START_MATCH\n")
        print("✅ START_MATCH envoyé au client")
        time.sleep(2)

        recv_buffer = ""
        conn.setblocking(False)  # Set the socket to non-blocking mode
        while True:
            recv_buffer, messages, closed = recevoir_messages_jsonl(conn, recv_buffer)

            if closed:
                break

            for message in messages:
                print("📨 Donnée reçue :", message)

            time.sleep(0.2)  # Simulate some processing time