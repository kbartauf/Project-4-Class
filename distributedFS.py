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
        # Meta Server

    def open(self, path, flags):
        # Meta Server

    def read(self, path, size, offset, fh):
         # Data Servers

    def readdir(self, path, fh):
        # Meta Server

    def readlink(self, path):
         # Data Servers

    def removexattr(self, path, name):
        # Meta Server

    def rename(self, old, new):
         # Data Servers
        # Meta Server

    def rmdir(self, path):
         # Data Servers
        # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        # Ignore Options
        # Meta Server

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
         # Data Servers
        # Meta Server

    def truncate(self, path, length, fh=None):
         # Data Servers
        # Meta Server

    def unlink(self, path):
         # Data Servers
        # Meta Server

    def utimens(self, path, times=None):
        # Meta Server

    def write(self, path, data, offset, fh):
         # Data Servers
        # Meta Server


def main():

    return


if __name__ == '__main__':
    main()
