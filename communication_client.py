#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import socket
import json
import time
import sys  
import subprocess
from ecrans_lcd import message_lcd
import SocketManager

#import keyboard  # Requires the 'keyboard' library to detect key presses

RASPBERRY_IP = '192.168.0.104'  
PORT = 65432

CONNECT_TIMEOUT = None

_start_time = None  # initialisé une seule fois

SocketManager.Init()
sock = SocketManager.CreateSocket()


def ping_raspberry(ip):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "1", ip], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def connexion_process() :

    handle = SocketManager.Connect(sock, RASPBERRY_IP, PORT, "balise")
    if handle == None : return None

    SocketManager.SendMessage(handle, "HELLO", timeout=CONNECT_TIMEOUT)
    if not handle.valid : return None

    msg = SocketManager.GetLatestMessage(handle, timeout=CONNECT_TIMEOUT)
    if not handle.valid : return None

    if msg != "ACK" : return None

    return handle
    
def attendre_connexion_serveur(ip, port, timeout_max=300, delai_retentative=1):
    """
    Essaie de se connecter à un serveur TCP toutes les `delai_retentative` secondes
    jusqu'à `timeout_max` secondes.

    Retourne True si le serveur est accessible, False sinon.
    """
    print(f"🔄 En attente que le serveur soit prêt sur {ip}:{port} (max {timeout_max}s) :", end="", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout_max:
        if ping_raspberry(ip):
            print("\n✅ Raspberry détecté !")
            return True
        print(".", end="", flush=True)
        time.sleep(delai_retentative)

    print("\n❌ Timeout : le serveur ne répond pas après", timeout_max, "secondes.")
    return False


def setup_connexion(lcd, timeout_max=300):
    """
    Attend que le serveur soit prêt, puis établit la connexion et retourne le socket.
    """
    
    """
    if not attendre_connexion_serveur(RASPBERRY_IP, PORT, timeout_max=timeout_max):
        print("⛔ Connexion impossible : le serveur n'a pas été détecté.")
        exit(1)  # Arrête le programme si le serveur n'est pas disponible
    """
    print("Connexion en cours...")
    handle = SocketManager.Connect(sock, RASPBERRY_IP, PORT, "balise", timeout=None)
    if handle == None : return None
    print("✅ Connecté au serveur")
    #time.sleep(2)  # Attendre un peu pour s'assurer que le serveur est prêt
    
    return handle

def verify_connexion(handle) :
    SocketManager.SendMessage(handle, "HELLO", timeout=None) # ← premier message
    msg_ack = SocketManager.GetNextMessage(handle, timeout=500)
    if msg_ack == "ACK":
        print("✅ Message de bienvenue reçu du serveur")

def send_data(handle, tas_detected):
    """Sends the tas_detected dictionary to the server."""
    json_data = json.dumps(tas_detected)
    SocketManager.SendMessage(handle, json_data)
    print("Données envoyées :", tas_detected)

def is_json_decodable(data):
    """
    Vérifie si une donnée est décodable en JSON.
    Retourne le JSON décodé si valide, sinon None.
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

def receive_couleur_equipe(handle, timeout=600):
    """
    Reçoit la couleur d'équipe depuis le serveur.
    Retourne la couleur ou None si timeout ou données invalides.
    """


    try:
        print("⏳5min Attente de la couleur de l'équipe...")
        data = SocketManager.GetLatestMessage(handle, timeout=timeout)

        couleur_equipe = is_json_decodable(data)

        if (couleur_equipe == "bleu") or (couleur_equipe == "jaune"):
            print("🎨 Équipe couleur reçue :", couleur_equipe)
            return couleur_equipe
        else:
            print("⚠️ Données reçues invalides :", data)
            return None
    except Exception as e :
        print(f"error getting team color : {str(e)}")
    
    """
    except socket.timeout:
        print("⚠️ Timeout en attente de la couleur de l'équipe")
        return None
    except ConnectionResetError:
        print("❌ Connexion réinitialisée par le serveur.")
        return None
    """
    


def couleur_equipe(handle, lcd):
    """
    Attend jusqu'à 10 minutes pour recevoir la couleur d'équipe.
    Si elle n'est pas reçue ou si la connexion est perdue, quitte le programme.
    """
    message_lcd(lcd,"couleur ???")
    couleur = receive_couleur_equipe(handle, timeout=600)  # 10 minutes
    if couleur:
        print(f"✅ Couleur de l'équipe confirmée : {couleur}")
        message_lcd(lcd,f"couleur {couleur}")
        return couleur
    else:
        print("❌ Aucune couleur d'équipe reçue dans le délai imparti ou erreur réseau.")
        handle.Close()
        sys.exit(1)

def exchange_infos(handle) :

    try :
        #SocketManager.DumpStoredMessages()
        msg = SocketManager.GetLatestMessage(handle)
        print(f"received {msg}")
        if msg != "START_MATCH" : return None
        SocketManager.SendMessage(handle, "WHAT_COLOR")
        msg = SocketManager.GetLatestMessage(handle)
        print(f"received {msg}")
        color = msg
        SocketManager.SendMessage(handle, "OK")
        print("sent ok")

        return color
    
    except :
        pass

def wait_start_match(handle):
    """
    Démarre le timer à la réception de START_MATCH.
    Retourne le temps écoulé depuis le début du match.
    """
    global _start_time

    if _start_time is None:
        print("⏳ Attente du signal de début de match...")
        data = SocketManager.GetLatestMessage(handle, timeout= 500)
        print("type data", type(data))
        print("data reçu singal match", repr(data))
        if data.strip() == "START_MATCH":
            print("✅ Signal de début de match reçu")
            _start_time = time.time()
            return 0.0
        else:
            print("⚠️ Signal non reconnu, attente...")
            time.sleep(1)
            return None
    else:
        elapsed = time.time() - _start_time
        return round(elapsed, 3)