#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

import json

import time

RASPBERRY_IP = '192.168.0.103'  
PORT = 65432

def setup_connexion():
    """Establishes a connection to the server and returns the socket."""
    print("Connexion en cours...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((RASPBERRY_IP, PORT))
    print("Connecté au serveur")
    return s

def send_data(socket_conn, tas_detected):
    """Sends the tas_detected dictionary to the server."""
    json_data = json.dumps(tas_detected)
    socket_conn.sendall(json_data.encode())
    print("Données envoyées :", tas_detected)

def receive_couleur_equipe(socket_conn, timeout=3):
    """
    Receives the team color from the server with an optional timeout.
    Returns the team color or None if a timeout occurs.
    """
    if timeout is not None:
        socket_conn.settimeout(timeout)

    try:
        data = socket_conn.recv(1024)
        couleur_equipe = json.loads(data.decode())
        print("Équipe couleur reçue :", couleur_equipe)
        return couleur_equipe
    except socket.timeout:
        print("⚠️ Timeout en attente de la couleur de l'équipe")
        return None
    finally:
        if timeout is not None:
            socket_conn.settimeout(None)  # Reset the timeout to default

def couleur_equipe(socket_conn):
    """
    Waits for the team color to be received.
    Loops until the team color is successfully received.
    Returns the team color.
    """
    while True:
        couleur = receive_couleur_equipe(socket_conn, timeout=2)  # Timeout of 2 seconds
        if couleur:
            print(f"Couleur de l'équipe confirmée : {couleur}")
            return True, couleur
        else:
            print("En attente de la couleur de l'équipe...")


