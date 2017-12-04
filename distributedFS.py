import xmlrpclib

class Memory(LoggingMixIn, Operations):

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(metaport)+"/")
        for iPort in iaDataPorts :
            self.data_proxy_array[i] = xmlrpclib.ServerProxy("http://localhost:"+str(iPort)+"/")

    def chmod(self, path, mode):
        # Meta Server

    def chown(self, path, uid, gid):
        # Meta Server

    def create(self, path, mode):
        # Meta Server

    def getattr(self, path, fh=None):
        # Meta Server

    def getxattr(self, path, name, position=0):
        # Meta Server

    def listxattr(self, path):
        # Meta Server

    def mkdir(self, path, mode):
         # Data Servers
        startServer = startHash(path)
        for i in data_server_array:
            self.data_server_array[(startServer+i)%numServers].mklist(path)
        # Meta Server

    def open(self, path, flags):
        # Meta Server

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

    def resolveBlkNum(fname,BlkNum):
        val = startHash(fname)
        serverNum = (val+BlkNum)%numServers
        return serverNum

    def rmdir(self, path):
        # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        # Ignore Options
        # Meta Server

    def startHash(fname):
        val = hash(fname)
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
            trunc = data_server_arrray[resolveBlkNum(path,floor(keep))].get(path,floor(keep)/numServers)
            for i in len((8-((keep-floor(keep))*8)):
                trunc[7-i] = None
                data_server_arrray[resolveBlkNum(path,floor(keep))].putOverwrite(path,trunc,floor(keep)/numServers)         
            
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
