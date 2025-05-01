#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import json

HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 65432      # Le même port que celui utilisé par le client

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[🔌] Serveur en attente de connexion sur le port {PORT}...")

    conn, addr = server_socket.accept()
    with conn:
        print(f"[✅] Connecté par {addr}")
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break  # Client a fermé la connexion
                decoded_data = json.loads(data.decode())
                print("[📥] Données reçues :", decoded_data)

            except json.JSONDecodeError:
                print("[⚠️] Erreur de décodage JSON.")
            except Exception as e:
                print("[❌] Erreur :", e)
                break
