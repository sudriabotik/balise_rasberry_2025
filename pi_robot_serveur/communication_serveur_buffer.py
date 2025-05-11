import SocketManager
import json
import time
import sys
import threading
from pi_robot_serveur.reception_serveur import recevoir_messages_jsonl

HOST = ''  # Listen on all available network interfaces
PORT = 65432

CONNECT_TIMEOUT = None

color = "bleu"

sock_host = SocketManager.CreateSocket()
infosSent = False # true if match start and color have been given to the beacon

SocketManager.StartHost(sock_host, PORT)

def ConnexionProcess() :

    handle = SocketManager.AwaitConnexion(sock_host, "host")
    if handle == None : return None

    msg = SocketManager.GetLatestMessage(handle)
    if not handle.valid :
        handle.Close()
        return None
    print("📥 Message reçu :", msg)

    if msg != "HELLO" :
        handle.Close()
        print("❌ Message de bienvenue non reconnu, fermeture de la connexion.")
        return None

    SocketManager.SendMessage(handle, "ACK")
    print("✅ Message de bienvenue envoyé au client ACK")
    if not handle.valid :
        handle.Close()
        return None

    return handle

def SendAllInfos(handle : SocketManager.ConnexionHandle) :

    global infosSent

    while True :

        try :
            SocketManager.DumpStoredMessages(handle)
            SocketManager.SendMessage(handle, "START_MATCH")
            msg = SocketManager.GetLatestMessage(handle)
            if msg != "WHAT_COLOR" : return
            SocketManager.SendMessage(handle, json.dumps(color))
            msg = SocketManager.GetLatestMessage(handle)
            if msg != "OK" : return

            infosSent = True
        
        except :
            return


print(f"🟢 Serveur en écoute sur le port {PORT}")

handle = ConnexionProcess()

print("✅ Connecté par", handle.address)

# wait indefinitely for a message
msg = SocketManager.GetLatestMessage(handle)

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

infoThread = threading.Thread(target=SendAllInfos, args=[handle])
infoThread.start()

# with SocketManager the timeout is set for each send / receive
# conn.setblocking(False)  # Set the socket to non-blocking mode
while True:
    #recv_buffer, messages, closed = recevoir_messages_jsonl(conn, recv_buffer)

    # verify connexion is still good

    if not handle.valid :

        handle.Close()
        try :
            handle = ConnexionProcess()
        except :
            pass

    if infosSent :
        SocketManager.ReadReceptionBuffer(handle, timeout=0)

        if not handle.valid :
            continue

        messages = SocketManager.DumpStoredMessages(handle)

        for message in messages:
            print("📨 Donnée reçue :", message)

        
    else :

        if not infoThread.is_alive() :

            infoThread = threading.Thread(target=SendAllInfos, args=[handle])
            infoThread.start()
    

    
    time.sleep(0.2)  # Simulate some processing time