import socket
import threading
import queue
import time
from datetime import datetime
import os

COMMAND_SEPARATOR = ','
MESSAGE_SEPARATOR = ";"
    

class Server :

    STATE_DISCONNECTED = 0
    STATE_CONNECTED = 1

    """ tickrate : how often the server refreshes in seconds """
    def __init__(self, tickrate : float, name : str, inQueue : queue.Queue, outQueue : queue.Queue, port : int) :

        self.tickrate = tickrate
        self.state = Server.STATE_DISCONNECTED
        self.stop = False

        self.inQueue = inQueue
        self.outQueue = outQueue
        self.messageBuffer = ""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", port))

        self.connexion = None
        self.address = None

        self.logFile = open(f"server_{name}.log", "a")

        self.Log("\n\n")
        self.Log("-- NEW RUN --")
        self.Log("\n")

    def Log(self, text : str) :
        self.logFile.write(f"[ {datetime.now().time()} ] {text}\n")
        self.logFile.flush() # sometimes the file may not be closed properly (BAU or program killed) ,
        #so it is important to flush for the data to be written right now


    """ The main loop """
    def Main(self) :

        while not self.stop :

            print("doing a loop")

            loopStartTime = time.time()

            try :
                while True :
                    command = self.GetNextCommand()
                    print(f"got command {command}")
                    if command == None : break
                    self.ExecuteCommand(command)
            except Exception as e :
                self.Log(f"error executing command : {str(e)}")
            

            if self.state == Server.STATE_DISCONNECTED :

                self.AwaitConnexion()
            
            elif self.state == Server.STATE_CONNECTED :

                self.GetMessages()
            
        

            time.sleep(max(0, loopStartTime - time.time() + self.tickrate))
        
        print(f"server ended {self.stop}")
        if self.connexion != None : self.connexion.close()
        self.sock.close()
        

    

    """ read what is requested of the server through the queue """
    def GetNextCommand(self) :
        try :
            message = self.inQueue.get_nowait()
            return message
        except queue.Empty :
            return None
        except Exception as e :
            self.Log(f"couldn't retrieve from input queue : {str(e)}")
            raise e
    
    def ExecuteCommand(self, command : str) :

        split = command.split(COMMAND_SEPARATOR)

        commandName = split[0]
        args = []
        if len(split) > 0 : args = split[1:]

        
        if commandName == "send" :
            self.SendMessage(args[0])
        
        else :
            raise ValueError(f"unrecognised command : {commandName}")
    
    def AwaitConnexion(self) :

        try :
            self.Log(f"awaiting a connexion")
            self.sock.settimeout(2) # wait to connect for 2 seconds before failing
            self.sock.listen()
            self.connexion, self.address = self.sock.accept()
            self.state = Server.STATE_CONNECTED
            self.Log(f"successfully connected to {str(self.address)}")
        except socket.error as error : # if the connexion time out the socket raises an error
            if error.errno != None : self.Log(f"couldn't connect : {os.strerror(error.errno)}")
            else : self.Log(f"couldn't connect : {error}")
        except Exception as e :
            self.Log(f"couldn't connect : {str(e)}")


    def SendMessage(self, message : str) :

        try :
            if self.connexion == None : raise RuntimeError("cannot send message, connexion is None")
            self.connexion.settimeout(0.5)
            self.connexion.sendall(message.encode())
            self.Log(f"sent message : {message}")
        except socket.error as error :
            if error.errno != None :
                self.Log(f"failed to send message : {os.strerror(error.errno)}")
                self.HandleSocketError(error.errno)
            else : self.Log(f"failed to send message : {error}")
        except Exception as e :
            self.Log(f"failed to send message : {str(e)}")
    

    """ read received messages and put them in the queue """
    def GetMessages(self) :

        try :
            self.connexion.settimeout(0.4)
            message = self.connexion.recv(1024)
            print(f"received : {message}")
            if message == None : return # early return
        except socket.error as error :
            if error.errno != None :
                self.Log(f"failed to receive messages : {os.strerror(error.errno)}")
                self.HandleSocketError(error.errno)
            else : self.Log(f"failed to receive messages : {error}")
            return
        except Exception as e :
            self.Log(f"failed to receive messages : {str(e)}")
            return
        
        
        try :
            # if there is a complete message in the buffer, put it in the queue
            self.messageBuffer += message.decode()
            split = self.messageBuffer.split(MESSAGE_SEPARATOR)
            self.messageBuffer = split[-1] # keep the end of the buffer

            # any found message put in the queue

            if len(split) > 1 :
                for i in range(0, len(split) - 1) :
                    self.outQueue.put_nowait(split[i])

        except queue.Full :
            self.Log("output queue is full")
        except Exception as e :
            self.Log(f"failed to put in the queue : {str(e)}")

    
    def HandleSocketError(self, errno : int) :

        if errno == 104 : # connexion reset by peer
            if self.connexion != None :
                self.connexion.close()
                self.connexion = None
                self.state == Server.STATE_DISCONNECTED
        elif errno == 32 : # broken pipe ??
            if self.connexion != None :
                self.connexion.close()
                self.connexion = None
                self.state == Server.STATE_DISCONNECTED


class ServerHandle :

    def __init__(self, serverInstance : Server, thread : threading.Thread, inQueue : queue.Queue, outQueue : queue.Queue, name : str) :

        self.serverInstance = serverInstance
        self.serverThread = thread
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.serverName = name

        self.serverThread.start()


def CreateNewServer(name : str, port : int) :

    try :
        inQueue = queue.Queue(2048)
        outQueue = queue.Queue(2048)
        server = Server(0.5, name, inQueue, outQueue, port)
        handle = ServerHandle(server, threading.Thread(target=Server.Main, args=[server]), inQueue, outQueue, name)

        return handle
    
    except Exception as e :

        print(f"failed to create the server : {str(e)}")


def SendMessage(handle : ServerHandle, message : str) :

    try :
        handle.inQueue.put_nowait(f"send,{message}")
        return True
    except Exception as e :
        print(f"couldn't put command in queue : {str(e)}")
        return False


def GetNextMessage(handle : ServerHandle) :

    try :
        msg = handle.outQueue.get_nowait()
        return msg
    except queue.Empty :
        return None
    
    except Exception as e :
        print(f"couldn't get next message : {str(e)}")


def IsConnected(handle : ServerHandle) :
    try :
        return handle.serverInstance.state == Server.STATE_CONNECTED
    except Exception as e :
        print(f"cannot know if server is connected : {e}")
        return False

def StopServer(handle : ServerHandle) :

    try :
        handle.serverInstance.stop = True
    except Exception as e :
        print(f"cannot stop server : {str(e)}")