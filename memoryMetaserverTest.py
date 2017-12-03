import sys
import xmlrpclib

class Memory():

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(iMetaPort)+"/")
#        for iPort in iaDataPorts :
#            self.data_proxy_array[i] = xmlrpclib.ServerProxy("http://localhost:"+str(iPort)+"/")

    def chmod(self, path, mode):
        return self.meta_proxy.chmod(path, mode) # Meta Server

    def chown(self, path, uid, gid):
        return self.meta_proxy.chown(path, uid, gid) # Meta Server

    def create(self, path, mode):
        return self.meta_proxy.create(path, mode) # Meta Server

    def getattr(self, path, fh=None):
        return self.meta_proxy.getattr(path) # Meta Server

    def getxattr(self, path, name, position=0):
        return self.meta_proxy.getxattr(path, name) # Meta Server

    def listxattr(self, path):
        return self.meta_proxy.listxattr(path) # Meta Server

    def mkdir(self, path, mode):
        # Data Servers
        return self.meta_proxy.mkdir(path, mode) # Meta Server

    def open(self, path, flags):
        return self.meta_proxy.open() # Meta Server

    def read(self, path, size, offset, fh):
        None
        # Data Servers

    def readdir(self, path, fh):
        return self.meta_proxy.readdir() # Meta Server

    def readlink(self, path):
        None
        # Data Servers

    def removexattr(self, path, name):
        return self.meta_proxy.removexattr(path, name) # Meta Server

    def rename(self, old, new):
        # Data Servers
        return self.meta_proxy.rename(old, new) # Meta Server

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
        self.meta_proxy.write(path, len(data), offset) # Meta Server


def main():

    if( len(sys.argv) < 3 ) :
        print('usage: %s <metaserver port> <dataserver ports)' % argv[0])
        return

    iDataPorts = []
    for i in range(2,len(sys.argv)) :
        iDataPorts.append( int(sys.argv[i]) )

    test = Memory( int(sys.argv[1]), iDataPorts)
    mode = 16

    print(test.readdir(None, None))

    # Test Making Directories (sub4_folder0)
    test.mkdir("/sub1_folder0/", mode)
    test.mkdir("/sub1_folder0/sub2_folder0/sub3_folder0/sub4_folder0", mode)
    test.mkdir("/sub1_folder0/sub2_folder0/sub3_folder1/", mode)
    print(test.readdir(None, None))

    # Test Making Files
    test.create("/sub1_folder0/test.txt", mode)
    test.create("/sub1_folder0/sub2_folder0/sub3_folder0/copy.txt",mode)
    test.create("/sub1_folder0/sub2_folder0/sub3_folder1/copy.txt",mode)
    test.create("/sub1_folder0/sub2_folder0/sub3_folder2/copy.txt",mode)
    print(test.readdir(None, None))

    # Test GetAttr / Utimens / chmod
    print(test.getattr("/sub1_folder0/test.txt"))
    test.chmod("/sub1_folder0/test.txt", 37)
    test.utimens("/sub1_folder0/test.txt", None)
    print(test.getattr("/sub1_folder0/test.txt"))

    # Test ListxAttr / chown / RemovexAttr(ON A CONFIRMED EXISTING ELEMENT)
    print(test.listxattr("/sub1_folder0/"))
    print(test.getxattr("/sub1_folder0/", 'st_uid'))
    test.chown("/sub1_folder0/",24,25)
    print(test.getxattr("/sub1_folder0/", 'st_uid'))
    test.removexattr("/sub1_folder0/", 'st_uid')
    print(test.listxattr("/sub1_folder0/"))

    # RemoveXAttr(On A Non Existing Element)

    # Test SetXAttr
    #test.setxattr(path, name, value, None)

    # Test Rename / Rmdir / Symlink
    print(test.readdir(None, None))
    test.rmdir("/sub1_folder0/sub2_folder0/sub3_folder1/")
    #test.rename()
    #test.symlink(target, source)
    print(test.readdir(None, None))

    # Test Unlink
    #test.unlink(path)

    # Test Open
    #test.open(None, None)

    # Test Length
    #test.truncate(path, length)
    #test.write(path, data, offset, None)

    return


if __name__ == '__main__':
    main()
