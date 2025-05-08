#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import Server

import json

import time

RASPBERRY_IP = '192.168.0.103'  
PORT = 65432

server_handle = None

def setup_server():
    
    global server_handle

    server_handle = Server.CreateNewServer("balise", PORT)


def send_data(socket_conn, tas_detected):
    """Sends the tas_detected dictionary."""
    json_data = json.dumps(tas_detected)
    
    Server.SendMessage(server_handle, json_data)

    print("Données envoyées :", tas_detected)

def receive_couleur_equipe(socket_conn, timeout=3):
    """
    Receives the team color from the server with an optional timeout.
    Returns the team color or None if a timeout occurs.
    """
    if timeout is not None:
        socket_conn.settimeout(timeout)

    """
    since the server is in another thread, cannot directly access the connexion or the timout
    the quickest solution is to make a timed loop that polls for the 
    """
    initial_time = time.time()



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


