#rock paper scissors game
#VERSION 1.0
import socket, sys, threading, time
serveraddr = ('127.0.0.1', 1337) #change to 82.41.135.121

#-----------------------CUSTOM EXCEPTIONS-------------------------

class DisconnectedError(Exception):
    '''Server disconnected'''
    pass
class PlayerLeft(Exception):
    '''Other player left'''
    pass
class ServerError(Exception):
    '''Received invalid data'''

#----------------------DATA FLOW MANAGEMENT-----------------------
    
#global vars to send messages btw threads
disconnected = False
playerleft = False
data = None
def recvdata(): #will be run as thread
    '''continuously read data from connection and check if
connection is maintained. Put data recieved in global variable'''
    global data, disconnected, playerleft
    while True:
        try: recv = client.recv(1024)
        except: disconnected = True; break
        recv = str(recv, 'ascii')
        if recv=='': disconnected = True; break
        elif recv=='player left\n': playerleft = True; continue
        else: data = recv
        while data: pass #wait for data to be empty

def getdata(): #not a thread
    '''Fetch data from connection -> return'''
    global data, disconnected, playerleft
    received = ''
    starttime = time.time()
    waited = False
    while True:
        if time.time()>starttime+20 and not waited:
            print('[-]Waiting...'); waited = True
        if data:
            received = data; data = None; break
        if disconnected: raise DisconnectedError()
        if playerleft: raise PlayerLeft()
    return received

def getuserinput():
    global send
    send = input('Your move (rock/paper/scissors): ').strip().lower()

#--------------------------------SETUP-------------------------
    
client = socket.socket()
print('[-]Connecting to server...')
try: client.connect(serveraddr)
except:
    print('[-]Sorry, server currently unavailable. Please try again later.')
    sys.exit(4) #error code 4: server unavailable
listener = threading.Thread(target=recvdata, name='listener')
listener.start()

#-----------------------------MAIN PROGRAM---------------------

while True:
    print('[-]Waiting for other players...')
    try:
        #wait for 'startgame'
        cmd = getdata()
        if cmd=='startgame\n': #check for correct command
            print('[-]Opponent found, starting game...')
            roundnum = 1
            while True: #rounds
                #wait for 'input'
                cmd = getdata()
                if cmd=='input\n': #check for correct command
                    #start round
                    print('ROUND', roundnum)
                    print('< Rock, paper, scissors! >')
                    #get valid input
                    send = ''
                    while send not in ('rock', 'paper', 'scissors'):
                        getinput = threading.Thread(target=getuserinput, name='input')
                        getinput.start()
                        while getinput.is_alive():
                            if disconnected: raise DisconnectedError()
                            if playerleft: raise PlayerLeft()
                    #send input to server
                    client.send(bytes(send, 'ascii'))
                    #get result from server
                    result = getdata()
                    print(result)
                    roundnum += 1
                else: raise ServerError()
        else: raise ServerError()
    except PlayerLeft:
        print('[-]Other player left the game')
        continue #back to start
    except DisconnectedError:
        print('[-]Connection lost. Please try again')
        sys.exit(2) #Error code 2: interruption
    except ServerError:
        print('[-]Server error: received invalid data')
        sys.exit(3) #Error code 3: server error
