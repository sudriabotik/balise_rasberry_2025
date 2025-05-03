#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import Server

import json

PORT = 65432



handle = Server.CreateNewServer("balise", PORT)

def send_data(tas_detected):
    """Sends the tas_detected dictionary to the server."""
    json_data = json.dumps(tas_detected)
    Server.SendMessage(handle, f"TAS/{json_data}")
    print("Données envoyées :", tas_detected)
