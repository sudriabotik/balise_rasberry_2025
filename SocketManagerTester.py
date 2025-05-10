import SocketManager

import threading
import time


SERVER_IP = "localhost"
PORT = 65432

SocketManager.Init()

clientSocket = SocketManager.CreateSocket()

hostSocket = SocketManager.CreateSocket()


def HostCode() :

    SocketManager.StartHost(hostSocket, PORT)

    handle = SocketManager.AwaitConnexion(hostSocket, "host", timeout=5)

    print(handle)

    for i in range(20) :

        SocketManager.SendMessage(handle, f"this is message {i}")
        if not handle.valid :
            print("connexion no longer valid")
            break
        time.sleep(1)
    
    time.sleep(5)

    handle.Close()


def ClientCode() :

    handle = SocketManager.Connect(clientSocket, SERVER_IP, PORT, "client", timeout=None)

    print(handle)

    time.sleep(5)

    while True :
        msg = SocketManager.GetNextMessage(handle)
        if not handle.valid :
            print("connexion no longer valid")
            break
        if msg == None :
            print("no more directly available messages, closing client")
            break
        print(msg)
    
    handle.Close()


hostThread = threading.Thread(target=HostCode)

clientThread = threading.Thread(target=ClientCode)

hostThread.start()
clientThread.start()

hostThread.join()
clientThread.join()

SocketManager.Stop()