import socket
from datetime import datetime
import traceback


lastErrCode = 0

def Init() :
    global mainLog
    mainLog = open("socket_manager.log", "a")
    mainLog.write("\n\n\n##### NEW RUN #####\n\n")

def Stop() :
    global mainLog
    mainLog.close()

def WriteToMainLog(content : str, error = True) :
    global mainLog
    string = f"{datetime.now().time()} : {content}\n"
    mainLog.write(string)
    mainLog.flush() # make sure the change are written right now, because the file might not be closed properly
    print(string, end="")
    if error : print(traceback.format_exc())



def CreateSocket() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock



def StartHost(sock : socket.socket, port : int) :
    sock.bind(("", port)) # listen to any ip address on the port


"""connexionName is just a name for the connexion log """
def AwaitConnexion(sock : socket.socket, connexionName : str, timeout = None) :
    

    try :
        sock.listen()
        sock.settimeout(timeout)
        connexion, address = sock.accept()
        handle = ConnexionHandle(connexion, connexionName)
        handle.address = address
        return handle

    except Exception as e :
        WriteToMainLog(f"couldn't get incoming connexion : {str(e)}")
        return None


"""connexionName is just a name for the connexion log """
def Connect(sock : socket.socket, ip : str, port : int, connexionName : str, timeout = None) :

    try :
        sock.settimeout(timeout)
        sock.connect((ip, port))
        handle = ConnexionHandle(sock, connexionName)
        handle.address = (ip, port)
        return handle
    except Exception as e :
        WriteToMainLog(f"couldn't connect to {ip}:{port} : {str(e)}")
        global lastErrCode
        lastErrCode = e.errno
        return None


    


""" just a class to store infos about a connexion with a logfile and a reception buffer """
class ConnexionHandle :

    def __init__(self, connexion : socket.socket, logFileName : str) :

        self.connexion = connexion # the object to use for sending and receiving, socket for a client and connexion for a host
        assert type(connexion) == socket.socket
        
        self.address = () # the address it is connected to, tuple (ip, port)

        self.receptionBuffer = "" # whenever we read the reception buffer, store incomplete messages in there
        self.messageBuffer = [] # list of full message received

        self.valid = True # starts off as valid when created. Become non-valid depending on error handling
        self.errorCode = -1 # the error code that caused the handle to become invalid, if there is one

        self.logFile = open(logFileName + ".log", "a")
        self.logFile.write("\n\n\n##### NEW RUN #####\n\n")
    
    def WriteToLog(self, content : str) :
        string = f"{datetime.now().time()} : {content}\n"
        self.logFile.write(string)
        self.logFile.flush() # make sure the change are written right now, because the file might not be closed properly
        print(string, end="")
    
    # close the connexion
    def Close(self) :
        try :
            self.connexion.close()
        except Exception as e :
            print(e)
    
    def CloseLog(self) :
        try :
            self.logFile.close()
        except Exception as e :
            print(e)


""" Use this instead of Connect if the handle already exist """
def Reconnect(handle : ConnexionHandle, ip : str, port : int, timeout = None) :
    handle.Close()
    
    sock = CreateSocket()
    handle.connexion = sock
    #sock = handle.connexion
    
    try :
        handle.connexion.settimeout(timeout)
        handle.connexion.connect((ip, port))
        handle.connexion = sock
        handle.address = (ip, port)
        handle.valid = True
        return handle
    except Exception as e :
        WriteToMainLog(f"couldn't connect to {ip}:{port} : {str(e)}")
        global lastErrCode
        lastErrCode = e.errno
        return None

def HandleConnexionErrors(handle: ConnexionHandle, errno: int):
    handle.WriteToLog(f"processing connexion error with errno : {errno}")

    # Tous les codes qui rendent la connexion inutilisable
    FATAL_ERRNOS = {9, 32, 10038, 10053, 10054, 10057, 104}

    if errno in FATAL_ERRNOS:
        handle.valid = False
        handle.errorCode = errno
        if errno == 9:
            handle.WriteToLog("socket invalidated")        # message spécial
        else:
            handle.WriteToLog("connexion invalidated")


def CreateSocket() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

""" return true if the image has been sent """

def SendMessage(
        handle: ConnexionHandle,
        message: str,
        *,
        end: str = "\n",
        timeout: float = 0,
        encoding: str = "utf-8"
) -> bool:
    """
    Envoie *message* suivi de *end* sur la connexion portée par *handle*.

    –  Retourne True en cas de succès, False sinon.
    –  Invalide systématiquement le handle quand l’envoi échoue.
    –  Journalise l’octet exact envoyé pour faciliter le débogage.
    """

    # ---------- pré-contrôles ----------
    if handle is None or not handle.valid:
        WriteToMainLog("SendMessage: handle is None or invalid")
        return False

    # ---------- préparation du payload ----------
    try:
        payload: bytes = (message + end).encode(encoding, errors="surrogatepass")
    except UnicodeEncodeError as exc:
        handle.WriteToLog(f"[{datetime.now().time()}] Encoding error: {exc}")
        handle.valid = False
        return False

    # Trace hexadécimal (ex.: "TX (5B) : 6c 6f 6c 6f 0a")
    #handle.WriteToLog(
    #    f"TX ({len(payload)}B) : {payload.hex(' ')}"
    #)

    # ---------- envoi ----------
    try:
        handle.connexion.settimeout(timeout)
        handle.connexion.sendall(payload)
        return True

    # ---------- gestion des erreurs ----------
    except socket.timeout:
        # pas bloquant : on ré-essaiera à la prochaine itération
        handle.WriteToLog("SendMessage timeout")
        return False

    except socket.error as err:
        HandleConnexionErrors(handle, err.errno)
        handle.WriteToLog(
            f"SendMessage socket.error {err.errno} : {err.strerror}"
        )
        return False

    except Exception as exc:
        handle.WriteToLog(f"SendMessage unexpected error: {exc}")
        handle.valid = False        # prudence
        return False


""" return the number of new messages that arrived """
def ReadReceptionBuffer(connexionHandle : ConnexionHandle, timeout = 0) :

    try :
        if connexionHandle == None :
            WriteToMainLog("error, connexionHandle is None")
            return -1
    except :
        return -1
    
    data = None

    try :
        connexionHandle.connexion.settimeout(timeout) # a timeout of 0 has the same affect as setblocking(False)
        data = connexionHandle.connexion.recv(1028)

    except socket.error as error :
        HandleConnexionErrors(connexionHandle, error.errno)
        connexionHandle.WriteToLog(f"Failed to receive : {error.strerror}")
    except Exception as e :

        connexionHandle.WriteToLog(f"Failed to receive : {str(e)}")
    
    if not data : # it means the connexion is broken
        connexionHandle.WriteToLog("received empty bit, connexion broken")
        connexionHandle.valid = False
        return -1
    
    # process the data
    data = data.decode()

    connexionHandle.receptionBuffer += data

    # add any found complete messages to the message list
    messages = connexionHandle.receptionBuffer.split("\n")
    connexionHandle.receptionBuffer = messages.pop(-1) # put the last bit of incomplete message back in the buffer

    if len(messages) == 0 : return 0

    for message in messages :
        connexionHandle.messageBuffer.append(message)
    
    return len(messages)

""" returns the oldest available message """
def GetNextMessage(connexionHandle : ConnexionHandle, update = True, timeout = None) :
    if update : ReadReceptionBuffer(connexionHandle, timeout)
    if len(connexionHandle.messageBuffer) == 0 : return None
    return connexionHandle.messageBuffer.pop(0)

""" return the newest available message """
def GetLatestMessage(connexionHandle : ConnexionHandle, update = True, timeout = None) :
    if update : ReadReceptionBuffer(connexionHandle, timeout)
    if len(connexionHandle.messageBuffer) == 0 : return None
    return connexionHandle.messageBuffer.pop(-1)

# give the list of all the stored messages, and clear the list in the handle
def DumpStoredMessages(connexionHandle : ConnexionHandle) :
    messages = connexionHandle.messageBuffer
    connexionHandle.messageBuffer = []
    return messages

