import socket
from datetime import datetime



def Init() :
    global mainLog
    mainLog = open("socket_manager.log", "a")
    mainLog.write("\n\n\n##### NEW RUN #####\n\n")

def Stop() :
    global mainLog
    mainLog.close()

def WriteToMainLog(content : str) :
    global mainLog
    string = f"{datetime.now().time()} : {content}\n"
    mainLog.write(string)
    mainLog.flush() # make sure the change are written right now, because the file might not be closed properly
    print(string, end="")



def CreateSocket() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock



def StartHost(sock : socket.socket, port : int) :
    sock.bind(("", port)) # listen to any ip address on the port


"""connexionName is just a name for the connexion log """
def AwaitConnexion(sock : socket.socket, connexionName : str, timeout = None) :
    sock.listen()
    sock.settimeout(timeout)

    try :
        connexion, address = sock.accept()
        handle = ConnexionHandle(connexion, connexionName)
        return handle

    except Exception as e :
        WriteToMainLog(f"couldn't get incoming connexion : {str(e)}")
        return None


"""connexionName is just a name for the connexion log """
def Connect(sock : socket.socket, ip : str, port : int, connexionName : str, timeout = None) :

    sock.settimeout(timeout)
    try :
        sock.connect((ip, port))
        return ConnexionHandle(sock, connexionName)
    except Exception as e :
        WriteToMainLog(f"couldn't connect to {ip}:{port} : {str(e)}")
        return None
    


""" just a class to store infos about a connexion with a logfile and a reception buffer """
class ConnexionHandle :

    def __init__(self, connexion : socket.socket, logFileName : str) :

        self.connexion = connexion # the object to use for sending and receiving, socket for a client and connexion for a host
        assert type(connexion) == socket.socket

        self.receptionBuffer = "" # whenever we read the reception buffer, store incomplete messages in there
        self.messageBuffer = [] # list of full message received

        self.valid = True # starts off as valid when created. Become non-valid depending on error handling

        self.logFile = open(logFileName + ".log", "a")
        self.logFile.write("\n\n\n##### NEW RUN #####\n\n")
    
    def WriteToLog(self, content : str) :
        string = f"{datetime.now().time()} : {content}\n"
        self.logFile.write(string)
        self.logFile.flush() # make sure the change are written right now, because the file might not be closed properly
        print(string, end="")
    
    def Close(self) :
        try :
            self.connexion.close()
            self.logFile.close()
        except Exception as e :
            print(e)



def HandleConnexionErrors(connexionHandle : ConnexionHandle, errno : int) :
    
    if errno == 104 : # connexion reset by peer
        connexionHandle.valid = False
    elif errno == 32 : # broken pipe ??
        connexionHandle.valid = False

def CreateSocket() :
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

""" return true if the image has been sent """
def SendMessage(connexionHandle : ConnexionHandle, message : str, end="\n", timeout = 0) :

    connexionHandle.connexion.settimeout(timeout)

    try :
        data = message + end
        data = data.encode()
        connexionHandle.connexion.sendall(data)
        return True
    
    except socket.error as error :
        HandleConnexionErrors(connexionHandle, error.errno)
        connexionHandle.WriteToLog(f"Failed to send message {message} : {error.strerror}")
        return False
    
    except Exception as e :
        connexionHandle.WriteToLog(f"Failed to send message {message} : {str(e)}")


""" return the number of new messages that arrived """
def ReadReceptionBuffer(connexionHandle : ConnexionHandle, timeout = 0) :

    connexionHandle.connexion.settimeout(timeout) # a timeout of 0 has the same affect as setblocking(False)
    data = None

    try :
        data = connexionHandle.connexion.recv(1028)

    except socket.error as error :
        HandleConnexionErrors(connexionHandle, error.errno)
        connexionHandle.WriteToLog(f"Failed to receive : {error.strerror}")
    except Exception as e :

        connexionHandle.WriteToLog(f"Failed to receive : {str(e)}")
    
    if not data : return 0 # do nothing if data is empty
    
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
def GetNextMessage(connexionHandle : ConnexionHandle, update = True) :
    if update : ReadReceptionBuffer(connexionHandle)
    if len(connexionHandle.messageBuffer) == 0 : return None
    return connexionHandle.messageBuffer.pop(0)

""" return the newest available message """
def GetNewestMessage(connexionHandle : ConnexionHandle, update = True) :
    if update : ReadReceptionBuffer(connexionHandle)
    if len(connexionHandle.messageBuffer) == 0 : return None
    return connexionHandle.messageBuffer.pop(-1)



