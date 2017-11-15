import xmlrpclib

class Memory(LoggingMixIn, Operations):

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(metaport)+"/")
#        for iPort in iaDataPorts :
#            self.data_proxy_array[i] = xmlrpclib.ServerProxy("http://localhost:"+str(iPort)+"/")

    def chmod(self, path, mode):
        self.meta_proxy.chmod(path, mode) # Meta Server

    def chown(self, path, uid, gid):
        self.meta_proxy.chown(path, uid, gid) # Meta Server

    def create(self, path, mode):
        self.meta_proxy.create(path, mode) # Meta Server

    def getattr(self, path, fh=None):
        self.meta_proxy.getattr(path) # Meta Server

    def getxattr(self, path, name, position=0):
        self.meta_proxy.getxattr(path, name) # Meta Server

    def listxattr(self, path):
        self.meta_proxy.listxattr(path) # Meta Server

    def mkdir(self, path, mode):
        # Data Servers
        self.meta_proxy.mkdir(path, mode) # Meta Server

    def open(self, path, flags):
        self.meta_proxy.open(path, flags) # Meta Server

    def read(self, path, size, offset, fh):
        # Data Servers

    def readdir(self, path, fh):
        self.meta_proxy.readdir(path) # Meta Server

    def readlink(self, path):
        # Data Servers

    def removexattr(self, path, name):
        self.meta_proxy.removexattr(path, name) # Meta Server

    def rename(self, old, new):
        # Data Servers
        self.meta_proxy.rename(old, new) # Meta Server

    def rmdir(self, path):
        # Data Servers
        self.meta_proxy.rmdir(path) # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        self.meta_proxy.setxattr(path, name, value) # Meta Server

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        # Data Servers
        self.meta_proxy.symlink(target, len(source)) # Meta Server

    def truncate(self, path, length, fh=None):
        # Data Servers
        self.meta_proxy.truncate(path, length) # Meta Server

    def unlink(self, path):
        # Data Servers
        self.meta_proxy.unlink(path) # Meta Server

    def utimens(self, path, times=None):
        self.meta_proxy.utimens(path, times) # Meta Server

    def write(self, path, data, offset, fh):
        # Data Servers
        self.meta_proxy.write(path, data, offset) # Meta Server


def main():

    if( len(sys.argv) < 3 )
        print('usage: %s <metaserver port> <dataserver ports)' % argv[0])

    iDataPorts = []
    for i in range(2,len(sys.argv)) :
        dataPorts.append( int(argv[i]) )

    test = memory( int(argv[1]), dataPorts)

    test.chmod(self, path, mode)
    test.chown(self, path, uid, gid)
    test.create(self, path, mode)
    test.getattr(self, path)
    test.getxattr(self, path, name)
    test.listxattr(self, path)
    test.mkdir(self, path, mode)
    test.open(self, path, flags)
    test.readdir(self, path, fh)
    test.removexattr(self, path, name)
    test.rename(self, old, new)
    test.rmdir(self, path)
    test.setxattr(self, path, name, value, options, position=0)
    test.symlink(self, target, source):
    test.truncate(self, path, length)
    test.unlink(self, path)
    test.utimens(self, path)
    test.write(self, path, data, offset, fh)

    return


if __name__ == '__main__':
    main()
