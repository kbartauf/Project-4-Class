import xmlrpclib

_SUCCESS = 0
_FAILURE = 1

class Memory():#LoggingMixIn, Operations):

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(iMetaport)+"/")
        for i in len(iaDataPorts) :
            self.data_proxy_array[i] = xmlrpclib.ServerProxy("http://localhost:"+str(iaDataPorts[i])+"/")

    def chmod(self, path, mode):
        self.meta_proxy.chmod(path, mode) # Meta Server
        return 0

    def chown(self, path, uid, gid):
        self.meta_proxy.chown(path, uid, gid) # Meta Server

    def create(self, path, mode):
        self.meta_proxy.create(path, mode) # Meta Server
        # [Data Server, Create Empty Lists]
        return self.meta_proxy.open() # Meta Server

    def getattr(self, path, fh=None):
        attrs = self.meta_proxy.getattr(path)
        if attrs == _FAILURE :
            raise FuseOSError(ENOENT)
        return attrs

    def getxattr(self, path, name, position=0):
        attrs = self.meta_proxy.getxattr(path, name) # Meta Server
        if attrs == _FAILURE :
            return '' # raise ENOATTR ?
        return attrs

    def listxattr(self, path):
        return self.meta_proxy.listxattr(path) # Meta Server

    def mkdir(self, path, mode):
        self.meta_proxy.mkdir(path, mode) # Meta Server

    def open(self, path, flags):
        return self.meta_proxy.open() # Meta Server

    def read(self, path, size, offset, fh):
         # Data Servers

    def readdir(self, path, fh):
        # Meta Server

    def readlink(self, path):
        # Data Servers
        startServer = startHash(path)
        k = 0
        filesize = float(self.meta_proxy.getxattr(path,'st_size'))
        fileLen = filesize/8.0
        numServers = float(numServers)
        for i in fileLen/numServers:
            for j in data_server_array
                data[k] = self.data_server_array[(startServer+j)%numServers].get(path,i)
                k += 1
        if fileLen/numServers - floor(fileLen/numServers) > 0:
            for n in len(((fileLen/numServers)-floor(fileLen/numServerss))*numServers))
                for j in data_server_array
                    data[k] = self.data_server_array[(startServer+j)%numServers].get(path,i)
                    k += 1
        return data

    def removexattr(self, path, name):
        # Meta Server

    def rename(self, old, new):
        # Data Servers
        for i in data_server_array:
            self.data_server_array.rename(old, new)
        # Meta Server

    def resolveBlkNum(path,BlkNum):
        val = startHash(path)
        serverNum = (val+BlkNum)%numServers
        return serverNum

    def rmdir(self, path):
        # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        # Ignore Options
        # Meta Server

    def startHash(path):
        val = hash(path)
        startVal = val%numServers
        return startVal 

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        # Data Servers
        # Meta Server

    def truncate(self, path, length, fh=None):
        # Data Servers
        startServer = startHash(path)
        length = float(length)
        bsize = float(bsize
        keep = length/bsize
        for i in data_server_array:
            self.data_server_array[(startServer+i)%numServers].truncateData(floor(keep))
        if (keep-floor(keep))) > 0
            trunc = self.data_server_arrray[resolveBlkNum(path,floor(keep))].get(path,floor(keep)/numServers)
            for i in len((8-((keep-floor(keep))*8)):
                trunc[7-i] = None
                self.data_server_arrray[resolveBlkNum(path,floor(keep))].putOverwrite(path,trunc,floor(keep)/numServers)         
            
        # Meta Server

    def unlink(self, path):
         # Data Servers
        startServer = startHash(path)
        for i in data_proxy_array:
            self.data_proxy_array[(startServer+i)%numServers].unlink(path)
        # Meta Server

    def utimens(self, path, times=None):
        # Meta Server

    def write(self, path, data, offset, fh):
        # Data Servers
        serverStart = startHash(path)
        filesize = float(self.meta_proxy.getxattr(path,'st_size'))
        fileLen = filesize/8
        block = offset/bsize
        pos = offset%bsize
        if (offset > filesize):
            for i in range(fileLen+1:block-1):
                self.data_server_array[i+resolveBlkNum(path,fileLen)].putAppend(path,[('/x00'*8)])
            i += 1
            self.data_server_array[i+resolveBlkNum(path,fileLen)].putAppend(path,[('/x00'*pos)+data[:(bsize-pos)])
            currentPOS = bsize-pos
   
            while currentPOS <= len(data):          
                i +=1
                self.data_server_array[i+resolveBlkNum(path,fileLen)].putAppend(path,[data[currentPOS:(currentPOS+8)]
                currentPOS += bsize
                if currentPOS+bsize > len(data):
                    currentPOS -= bsize
                    i += 1
                    self.data_server_array[i+resolveBlkNum(path,fileLen)].putAppend(path,[data[(bsize-currentPOS):]+('/x00'*(bsize-(len(data)-currentPOS))]
                
        else:
           if (offset%bsize) != 0:
               self.data_server_array[resolve(path,offset%bsize)].putOverwrite(path,data[:(bsize-pos)]
           while currentPOS <= len(data):          
                i +=1
                self.data_server_array[i+resolveBlkNum(path,fileLen)].putOverwrite(path,[data[currentPOS:(currentPOS+8)]
                currentPOS += bsize
                if currentPOS+bsize > len(data):
                    currentPOS -= bsize
                    if len(offset)+len(data) <= filesize:
                        i += 1
                        temp = self.data_server_array[i+resolveBlkNum(path,fileLen)].get(path,(offset+len(data)-1)/bsize))
                       temp =  temp[:(len(data)-currentPOS)] + data[currentPOS:]
                    else:
                    i += 1
                    self.data_server_array[i+resolveBlkNum(path,fileLen)].putAppend(path,[data[(bsize-currentPOS):]+('/x00'*(bsize-(len(data)-currentPOS))] 
              
                    
def main():
    numServers = len(sys.argv)-2
    bsize = 8
    if( len(sys.argv) < 6 ) :
        print('usage: %s <metaserver port> <dataserver ports)' % argv[0])
        return

    iDataPorts = []
    for i in range(2,len(sys.argv)) :
        iDataPorts.append( int(sys.argv[i]) )

    test = Memory( int(sys.argv[1]), iDataPorts)

    test.    
    

    return


if __name__ == '__main__':
    main()
