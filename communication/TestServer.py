import Server
import time


PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


server = Server.Server(PORT, "server_log.txt")

list = ["1" for i in range(8)]

while True :
    result = None
    try :
        result = server.SendList(list)
        if result == True : print("successfully sent the stuff")
        else : time.sleep(1)
    except Exception as e :
        print(str(e))
        time.sleep(1)
    
    print(f"waiting {result}")


