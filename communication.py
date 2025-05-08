#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import SocketManager

import json

import time

RASPBERRY_IP = '192.168.0.103'  
PORT = 65432

SocketManager.Init()

sock = SocketManager.CreateSocket()
SocketManager.StartHost(sock, PORT)

connexion_handle = None

def await_connexion():
	
	global connexion_handle
	
	print("Connexion en cours...")
	connexion_handle = SocketManager.AwaitConnexion(sock, "balise")
	print("Connected")
	


def send_data(socket_conn, tas_detected):
	"""Sends the tas_detected dictionary."""
	json_data = json.dumps(tas_detected)
	
	SocketManager.SendMessage(connexion_handle, json_data)

	print("Données envoyées :", tas_detected)

def receive_couleur_equipe(socket_conn, timeout=3):
	"""
	Receives the team color from the server with an optional timeout.
	Returns the team color or None if a timeout occurs.
	"""
	
	SocketManager.GetNewestMessage(connexion_handle)

	try:
		data = socket_conn.recv(1024)
		couleur_equipe = json.loads(data.decode())
		print("Équipe couleur reçue :", couleur_equipe)
		return couleur_equipe
	
	except socket.timeout:
		print("⚠️ Timeout en attente de la couleur de l'équipe")
		return None




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


