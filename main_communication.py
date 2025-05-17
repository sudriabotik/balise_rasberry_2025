from communication_client import create_handle, setup_connexion, connexion_process, send_data, couleur_equipe, wait_start_match, exchange_infos

import time
import SocketManager

connexion_handle = create_handle()

# Boucle pour attendre la réception de la couleur de l'équipe
couleur_equipe_value = None
#couleur_equipe_value = couleur_equipe(connexion_handle, lcd)
#print(f"Couleur de l'équipe reçue : {couleur_equipe_value}")

# Boucle principale pour traiter les images
while True:
    # verify connexion is still ok, else attempt to reconnect
    print(connexion_handle)
    if connexion_handle == None :
        print("this shouldn't happen")
    else :
        if not connexion_handle.valid :
            print("invalid connexion handle RECONNECTING ")
            connexion_handle.Close() # we do not really care of this cause an error, it's just to try to close it just in case
            connexion_process(connexion_handle)
    
    
    if couleur_equipe_value == None : # it means the match has not yet started
        couleur_equipe_value = exchange_infos(connexion_handle)
        if couleur_equipe_value != None : # this mean the robot sent that the match have started
            start_time = time.time()
            print(f"match started, with color {couleur_equipe_value}")
        else :
            print("failed to obtain informations from the robot")
            time.sleep(1)
            continue
    
    SocketManager.SendMessage(connexion_handle, "lolo")

    time.sleep(2)
    print("_______________________________")
    continue 

