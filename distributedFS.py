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
        # Meta Serverp4-
    	p = self.traverse(path)
        d, d1 = self.traverseparent(path, True)
        if offset > p['st_size']:
            d[d1] = [(d[d1][i] if i < len(d[d1]) else '').ljust(bsize, '\x00') for i in range(offset//bsize)] \
                    + [(d[d1][offset/bsize][:offset % bsize] if offset//bsize < len(d[d1]) else '').ljust(offset % bsize, '\x00')]
        size = len(data)
        sdata = [data[:bsize - (offset % bsize)]] + [data[i:i+bsize] for i in range(bsize - (offset % bsize), size, bsize)]
        blks = range(offset//bsize, (offset + size - 1)//bsize + 1)
        mod = blks[:]
        mod[0] = (d[d1][blks[0]][:offset % bsize] if blks[0] < len(d[d1]) else '').ljust(offset % bsize, '\x00') + sdata[0]
        if len(mod[0]) != bsize and blks[0] < len(d[d1]):
            mod[0] = mod[0] + d[d1][blks[0]][len(mod[0]):]
        mod[1:-1] = sdata[1:-1]
        if len(blks) > 1:
            mod[-1] = sdata[-1] + (d[d1][blks[-1]][len(sdata[-1]):] if blks[-1] < len(d[d1]) else '')
        d[d1][blks[0]:blks[-1] + 1] = mod
        p['st_size']= offset + size if offset + size > p['st_size'] else p['st_size']
        return size

def main():

    return


if __name__ == '__main__':
    main()
