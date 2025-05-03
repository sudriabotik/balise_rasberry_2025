import socket
import time
import threading
from datetime import datetime



# no error handling in the class, remember to use it in try / catch blocks
class Server :

    def __init__(self, port, logfile : str) :

        self.connexion = None
        self.address = None
        self.currentThread = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", port))

        self.NewTask(threading.Thread(target=Server.__AwaitConnexion, args=[self]), "wait_connexion")

        self.logFile = open(logfile, "a")
        self.logFile.write(f"\n\n\nnew run at  {datetime.now()}  - - - - - - - - - - -\n\n")
    
    def __del__(self) :
        if self.connexion != None : self.connexion.close()
        if self.socket != None : self.socket.close()
        self.Log("server closed")
    
    def Log(self, text : str) :
        self.logFile.write(f"[ {datetime.now().time()} ] {text}\n")
        self.logFile.flush()
    
    def NewTask(self, thread : threading.Thread, name) :
        if self.currentThread != None : self.currentThread.join()
        self.currentThread = thread
        thread.start()
        self.currentTask = name
    

    def __AwaitConnexion(self) :

        self.socket.listen()
        self.socket.settimeout(None)
        self.connexion, self.address = self.socket.accept()
        self.currentTask = None
        self.Log(f"connected to {str(self.address)}")
    
    def SendList(self, list) :

        if self.currentThread.is_alive() : return self.currentTask

        string = ','.join(map(str, list))
        string += ";"

        try :
            self.socket.settimeout(2)
            self.connexion.sendall(string.encode())
            return True
        except socket.error as e :

            self.Log(str(e))
            
            self.HandleSocketError(e.errno)

            return False
    
    def HandleSocketError(self, errno : int) :

        if errno == 104 : # connexion reset by peer
            self.connexion.close()
            self.connexion = None
            self.NewTask(threading.Thread(target=Server.__AwaitConnexion, args=[self]), "reconnect") # attempt reconnect
        elif errno == 32 : # broken pipe ??
            self.connexion.close()
            self.connexion = None
            self.NewTask(threading.Thread(target=Server.__AwaitConnexion, args=[self]), "reconnect") # attempt reconnect
