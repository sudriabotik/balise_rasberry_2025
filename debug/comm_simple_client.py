import socket
import json

HOST = '192.168.0.103'  # Adresse IP du serveur
PORT = 65432       # Le même port que celui utilisé par le serveur

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("[🔗] Connecté au serveur.")

    try:
        # Exemple de données à envoyer
        data_to_send = {"message": "Bonjour, serveur!", "timestamp": "2025-05-04T12:00:00"}
        client_socket.sendall(json.dumps(data_to_send).encode())
        print("[📤] Données envoyées :", data_to_send)
    except Exception as e:
        print("[❌] Erreur lors de l'envoi des données :", e)