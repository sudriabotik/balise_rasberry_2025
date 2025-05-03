import Server

import time

PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# initialize

handle = Server.CreateNewServer("balise", PORT)

count = 0
while True :

    while True :
        message = Server.GetNextMessage(handle)

        if message != None :

            print(f"got message : {message}")
        
        else :
            break
    
    if Server.IsConnected(handle) :
        result = Server.SendMessage(handle, f"this is message number {count}")
        print(f'sending a message, {result}')
    print(Server.IsConnected(handle))
    count += 1
    time.sleep(0.5)
