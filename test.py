
server = {}    
numServers = 4

#working
def hash(fname,numServers):
    val = 0
    for pos in range(len(fname)):
        val = val + ord(fname[pos])
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


#working
def resolveBlkNum(fname,BlkNum):
    val = hash(fname, numServers)
    serverNum = (val+BlkNum)%numServers
    return serverNum

def put(blk, serverNum):
    server[serverNum] = [blk]
        
def main():
    name = 'ABC.txt'
    start = hash(name,numServers)
    #distributePacket(start, 'ABC,txt')
    serverNum = resolveBlkNum('ABC.txt', 14) 
    print(serverNum)   
    return
    

if __name__ == '__main__':
    main()
