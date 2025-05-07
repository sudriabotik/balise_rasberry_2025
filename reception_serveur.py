# reception.py

import json
import select

def recevoir_messages_jsonl(conn, recv_buffer):
    """
    Lit les messages JSONL disponibles sur la socket `conn`.
    
    Args:
        conn (socket.socket): la socket connectée au client.
        recv_buffer (str): le tampon de réception en cours.
    
    Returns:
        tuple:
            - new_buffer (str): le buffer mis à jour (partie incomplète gardée)
            - messages (list): liste des dictionnaires JSON reçus
            - closed (bool): True si la connexion a été fermée par le client
    """
    messages = []
    closed = False

    readable, _, _ = select.select([conn], [], [], 0)
    if conn in readable:
        try:
            data = conn.recv(16384)
            if data:
                recv_buffer += data.decode()
                lines = recv_buffer.split("\n")
                recv_buffer = lines.pop()  # on garde la dernière ligne incomplète

                for line in lines:
                    if not line.strip():
                        continue
                    try:
                        json_data = json.loads(line)
                        messages.append(json_data)
                    except json.JSONDecodeError as e:
                        print("❌ JSON invalide :", e)
            else:
                print("⚠️ Connexion vide : le client est encore connecté.")
        except ConnectionResetError:
            print("❌ Connexion réinitialisée par le client.")
            closed = True
    else:
        print("⏳ Rien à lire, on attend 15 secondes...")

    return recv_buffer, messages, closed
