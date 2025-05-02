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
