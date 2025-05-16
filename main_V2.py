
from communication_client import create_handle, setup_connexion, connexion_process, send_data, couleur_equipe, wait_start_match, exchange_infos
import time
import SocketManager


# ------------------- PRÉPARATION ----------------------------------------
connexion_handle = create_handle()      # (hors diagramme) – on part d’un handle “invalid”
couleur_equipe_value = None             # (hors diagramme)

# =================== BOUCLE PRINCIPALE ==================================
while True:
    print("dans la boucle principale")

    # [ A ] « connexion OK ? »  ------------------------------------------
    # ————————————————————————————————————————————————————————
    if connexion_handle is None:                   # cas impossible → message d’erreur
        print("this shouldn't happen")
    else:
        if not connexion_handle.valid:             # → connexion KO
            print("invalid connexion handle")
            connexion_handle.Close()               # ferme l’ancienne socket
            connexion_process(connexion_handle)    # ---(Connect/Reconnect)---+

    # [ B ] « match started ? »  ------------------------------------------------
    # ————————————————————————————————————————————————————————————————
    if couleur_equipe_value is None:               # match pas encore lancé
        # [ C ] exchange_infos() (Attend "start_match:<couleur>")
        couleur_equipe_value = exchange_infos(connexion_handle)

        if couleur_equipe_value is not None:       # → match démarré
            start_time = time.time()
            print(f"match started, with color {couleur_equipe_value}")
        else:                                      # [ D ] +--- non ---> sleep(1)
            print("failed to obtain informations from the robot")
            time.sleep(1)
            continue                               # retourne en haut de la boucle

    # [ E ] SendMessage("lolo")  ------------------------------------------------
    print(f"match started, with color {couleur_equipe_value}")
    print("lala")
    SocketManager.SendMessage(connexion_handle, "lolo")

    time.sleep(2)                                  # tempo avant le prochain tour
    print("_______________________________")
    #  boucle vers le début
