import SocketManager
import json
import time
import sys
import select
from pi_robot_serveur.reception_serveur import recevoir_messages_jsonl

HOST = ''  # Listen on all available network interfaces
PORT = 65432

sock_host = SocketManager.CreateSocket()

SocketManager.StartHost(sock_host, PORT)

print(f"🟢 Serveur en écoute sur le port {PORT}")
handle = SocketManager.AwaitConnexion(sock_host, "host")


print("✅ Connecté par", handle.address)

# wait indefinitely for a message
msg = SocketManager.GetLatestMessage(handle)
print("📥 Message reçu :",repr(msg))
if msg == "HELLO":
    SocketManager.SendMessage(handle, "ACK")
    print("✅ Message de bienvenue envoyé au client ACK")
else:
    print("❌ Message de bienvenue non reconnu, fermeture de la connexion.")
    handle.Close()
    sys.exit(1)

# Attente de 30 secondes avant d'envoyer la couleur
print("⏳ Attente de 10 secondes avant d'envoyer la couleur...")
time.sleep(10)

couleur = "bleu"
SocketManager.SendMessage(handle, json.dumps(couleur))
print("🎨 Couleur envoyée :", couleur)

print("⏳ Attente de 15 secondes avant d'envoyer START_MATCH...")
time.sleep(15)
SocketManager.SendMessage(handle, "START_MATCH")
print("✅ START_MATCH envoyé au client")
time.sleep(2)

recv_buffer = ""
# with SocketManager the timeout is set for each send / receive
# conn.setblocking(False)  # Set the socket to non-blocking mode
while True:
    #recv_buffer, messages, closed = recevoir_messages_jsonl(conn, recv_buffer)
    SocketManager.ReadReceptionBuffer(handle, timeout=0)

    if not handle.valid :
        break

    messages = SocketManager.DumpStoredMessages(handle)

    for message in messages:
        print("📨 Donnée reçue :", message)

    time.sleep(0.2)  # Simulate some processing time