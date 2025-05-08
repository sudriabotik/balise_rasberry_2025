#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import socket
import json
import time
import sys  
import subprocess

import SocketManager

#import keyboard  # Requires the 'keyboard' library to detect key presses

RASPBERRY_IP = '192.168.0.103'  
PORT = 65432

_start_time = None  # initialisé une seule fois

SocketManager.Init()
sock = SocketManager.CreateSocket()


def ping_raspberry(ip):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "1", ip], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    
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


def setup_connexion(timeout_max=300):
    """
    Attend que le serveur soit prêt, puis établit la connexion et retourne le socket.
    """
    if not attendre_connexion_serveur(RASPBERRY_IP, PORT, timeout_max=timeout_max):
        print("⛔ Connexion impossible : le serveur n'a pas été détecté.")
        exit(1)  # Arrête le programme si le serveur n'est pas disponible

    print("Connexion en cours...")
    handle = SocketManager.Connect(sock, RASPBERRY_IP, PORT, "balise", timeout=None)
    if handle == None : return None
    print("✅ Connecté au serveur")
    time.sleep(2)  # Attendre un peu pour s'assurer que le serveur est prêt
    
    return handle

def verify_connexion(handle) :
    SocketManager.SendMessage(handle, "HELLO", timeout=None) # ← premier message
    msg_ack = SocketManager.GetNewestMessage(handle, timeout=None)
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
        return json.loads(data.decode())
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
    


def couleur_equipe(handle):
    """
    Attend jusqu'à 10 minutes pour recevoir la couleur d'équipe.
    Si elle n'est pas reçue ou si la connexion est perdue, quitte le programme.
    """
    couleur = receive_couleur_equipe(handle, timeout=600)  # 10 minutes
    if couleur:
        print(f"✅ Couleur de l'équipe confirmée : {couleur}")
        return couleur
    else:
        print("❌ Aucune couleur d'équipe reçue dans le délai imparti ou erreur réseau.")
        handle.Close()
        sys.exit(1)

def wait_start_match(socket_conn):
    """
    Démarre le timer à la réception de START_MATCH.
    Retourne le temps écoulé depuis le début du match.
    """
    global _start_time

    if _start_time is None:
        print("⏳ Attente du signal de début de match...")
        data = socket_conn.recv(1024)
        if data == b"START_MATCH\n":
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