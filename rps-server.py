#rock paper scissors server
#VERSION 1.0
import socket, threading, multiprocessing, datetime, sys

#------------------------CUSTOM EXCEPTIONS--------------------------

class ConnectionClosed1(Exception):
    '''Player1 has left the game'''
    pass
class ConnectionClosed2(Exception):
    '''Player2 has left the game'''
    pass

#--------------------------SETUP LOGGING----------------------------

_logfile = 'rps.log'
with open(_logfile, 'a') as logfile:
    print('-------------------------------', file=logfile)
    print('Restarted {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), file=logfile)
    print('-------------------------------', file=logfile)
def log(msg):
    with open(_logfile, 'a') as logfile:
        print(msg, file=logfile)
    print(msg)

#-------------------------------------------------------------------

#still unused - need GUI
def quit():
    with open(_logfile, 'a') as logfile:
        logfile.write('Quit on {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    try: conn1.send('Quit')
    except: pass
    try: conn2.send('Quit')
    except: pass
    sys.exit(0)

#--------------------------DATA FLOW CONTROL-----------------------

#connclosed flags to pass data btw threads and main
connclosed1 = True
connclosed2 = True

#continuously read data from connections and check that still open
#then write to global variable
def getdata1():
    global data1, connclosed1
    while True:
        if not connclosed1:
            try: data = conn1.recv(1024)
            except: connclosed1 = True; continue
            data = str(data, 'ascii')
            if data=='': connclosed1 = True
            else: data1 = data
            while data1:
                continue

def getdata2():
    global data2, connclosed2
    while True:
        if not connclosed2:
            try: data = conn2.recv(1024)
            except: connclosed2 = True; continue
            data = str(data, 'ascii')
            if data=='': connclosed2 = True
            else: data2 = data
            while data2:
                continue

def getconnection2():
    global conn2, addr2
    conn2, addr2 = server.accept()

#-----------------------------SETUP------------------------------

server = socket.socket()
server.bind(('0.0.0.0', 1337))
server.listen(2)
getData1 = threading.Thread(target=getdata1, name='getdata1')
getData2 = threading.Thread(target=getdata2, name='getdata2')
getData1.start()
getData2.start()

#-------------------------MAIN PROGRAM---------------------------

while True:
    log('[-]Waiting for players...')
    conn1, addr1 = server.accept()
    connclosed1 = False
    log('[-]Connected to '+addr1[0]+' on port '+str(addr1[1])+' as Player 1')
    while True:
        log('[-]Waiting for Player 2...')
        getconn2 = threading.Thread(target=getconnection2, name='getconn2')
        getconn2.start()
        try:
            while True:
                if not getconn2.is_alive():
                    break
                if connclosed1:
                    raise ConnectionClosed1()
        except ConnectionClosed1:
            log('[-]Player 1 disconnected')
            break #go back to outer loop - back to start
        
        log('[-]Connected to '+addr2[0]+' on port '+str(addr2[1])+' as Player 2')
        connclosed2 = False
        log('[-]Starting game')
        conn1.send(bytes('startgame\n','ascii'))
        conn2.send(bytes('startgame\n','ascii'))
        try:
            while True:
                log('[-]Starting round')
                try: conn1.send(bytes('input\n', 'ascii'))
                except: raise ConnectionClosed1()
                try: conn2.send(bytes('input\n', 'ascii'))
                except: raise ConnectionClosed2()
                #wait until recieve input from both
                data1 = None; data2 = None
                player1 = ''; player2 = ''
                while True:
                    #implicit conversion to bool checks if there is something
                    #inside; the getdata threads are recving from tcp and
                    #writing to data vars
                    if data1:
                        player1 = data1
                        data1 = None
                    if data2:
                        player2 = data2
                        data2 = None
                    if player1 and player2:
                        break
                    if connclosed1: raise ConnectionClosed1()
                    if connclosed2: raise ConnectionClosed2()
                
                #calculate result of game
                if player1=='rock':
                    if player2=='rock':
                        result = 'Draw!'
                    elif player2=='paper':
                        result = 'Paper beats rock. $p2win'
                    elif player2=='scissors':
                        result = 'Rock beats scissors. $p1win'
                    else:
                        result = 'Error'
                elif player1=='paper':
                    if player2=='rock':
                        result = 'Paper beats rock. $p1win'
                    elif player2=='paper':
                        result = 'Draw!'
                    elif player2=='scissors':
                        result = 'Scissors beat paper. $p2win'
                    else:
                        result = 'Error'
                elif player1=='scissors':
                    if player2=='rock':
                        result = 'Rock beats scissors. $p2win'
                    elif player2=='paper':
                        result = 'Scissors beat paper. $p1win'
                    elif player2=='scissors':
                        result = 'Draw!'
                    else:
                        result = 'Error'
                else:
                    result = 'Error'
                result0 = result.replace('$p2win', 'Player 2 won.').replace('$p1win', 'Player 1 won.')
                result1 = result.replace('$p2win', 'You lose!').replace('$p1win', 'You win!\n')
                result2 = result.replace('$p2win', 'You win!').replace('$p1win', 'You lose!\n')
                log('[-]'+result0)
                try: conn1.send(bytes(result1, 'ascii'))
                except: raise ConnectionClosed1()
                try: conn2.send(bytes(result2, 'ascii'))
                except: raise ConnectionClosed2()
        except ConnectionClosed1:
            log('[-]Player 1 disconnected')
            conn1.close()
            conn1 = conn2; addr1 = addr2 #change player 2 to player 1
            log('[-]Player 2 '+str(addr1)+' is now Player 1')
            conn1.send(bytes('player left\n','ascii'))
            continue #back to start of inner loop (dont go all the way back)
        except ConnectionClosed2:
            log('[-]Player 2 disconnected')
            conn2.close()
            #dont need to change connection as player 1 is still there
            conn1.send(bytes('player left\n','ascii'))
            continue
