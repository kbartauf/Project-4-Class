
server = {}    
numServers = 4

def startHash(fname):
    val = hash(fname)
    startVal = val%numServers
    return startVal  

#needs put to work
#Need to check for packet destination success
#If server fails during data send, no way to know/stop as of now
def distributePacket(startVal, fname):
    for i in range(2):
        for pos in range(len(fname)):
            put(fname[pos+i], (startVal+pos+i)%numServers)
    return

def resolveBlkNum(fname,BlkNum):
    val = startHash(fname)
    serverNum = (val+BlkNum)%numServers
    return serverNum

def put(blk, serverNum):
    server[serverNum] = [blk]
        
def main():
    '''
        name = 'ABC.txt'
        start = startHash(name)
        #distributePacket(start, 'ABC,txt')
        serverNum = resolveBlkNum('ABC.txt', 15) 
        print(start)
        print(serverNum)   
    '''
    a = 150
    b = 8
    a = float(a)
    b = float(b)
    c = a/b
    print(c)    
    return
    

if __name__ == '__main__':
    main()
