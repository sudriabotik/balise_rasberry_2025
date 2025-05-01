#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

import json

import time



RASPBERRY_IP = '192.168.0.103'  

PORT = 65432



data_to_send = {

    "tas_1": ["1"],

    "tas_2": ["0"],

    "tas_3": ["1"],

    "tas_4": ["1"],

    "tas_5": ["1"],

    "tas_6": ["0"],

    "tas_7": ["0"],

    "tas_8": ["1"]

}



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((RASPBERRY_IP, PORT))

    print(" Connecté au serveur")



    while True:

        json_data = json.dumps(data_to_send)

        s.sendall(json_data.encode())

        print(" Donne envoye")

        time.sleep(0.5)     
