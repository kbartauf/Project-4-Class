import sys
import xmlrpclib

_SUCCESS = 0
_FAILURE = 1

_BLOCKSIZE = 8

class Memory():#LoggingMixIn, Operations):

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(iMetaPort)+"/")
        self.data_proxy_array = []
        for i in range(0,len(iaDataPorts)) :
            self.data_proxy_array.append( xmlrpclib.ServerProxy("http://localhost:"+str(iaDataPorts[i])+"/") )
        self.number_data_servers = len(iaDataPorts)

    # Helper Functions #

    def startHash(self, path):
        return (hash(path)%self.number_data_servers)

    def appendBlock(self, block_start, block_number, pathname, string ):
        return self.data_proxy_array[ (block_start+block_number)%self.number_data_servers ].putAppend(pathname,string)

    def overwriteBlock(self, block_start, block_number, pathname, string):
        return self.data_proxy_array[ (block_start+block_number)%self.number_data_servers ].putOverwrite(   pathname, 
                                                                                                        string, 
                                                                                                    block_number/self.number_data_servers)

    def readBlock(self, block_start, block_number, pathname ):
        #print("self.data_proxy_array[")
        #print( (block_start+block_number)%self.number_data_servers )
        #print("].get(")
        #print(pathname)
        #print(block_number/self.number_data_servers)
        #print(");")

        return self.data_proxy_array[ (block_start+block_number)%self.number_data_servers ].get(    pathname,
                                                                                                    block_number/self.number_data_servers)



    #def readRepair(self, serverStart, block_number, pathname ):


    # Memory Functions #

    def chmod(self, path, mode):
        self.meta_proxy.chmod(path, mode) # Meta Server
        return 0

    def chown(self, path, uid, gid):
        self.meta_proxy.chown(path, uid, gid) # Meta Server

    def create(self, path, mode):
        self.meta_proxy.create(path, mode) # Meta Server
        # [Data Server, Create Empty Lists]
        #return self.meta_proxy.open() # Meta Server

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

#    def read(self, path, size, offset, fh):
        # Data Servers

    def readdir(self, path, fh):
        return self.meta_proxy.readdir() # Meta Server
        # Add Slashes Probably

    def readlink(self, path):
        filesize = self.meta_proxy.getxattr(path,'st_size')
        if filesize == 0 :
            return ""

        number_blocks = ((filesize-1)/_BLOCKSIZE)   #EG: Filesize=9, numberblocks=1, i=[0], 1 
        serverStart = self.startHash(path)          #EG: Filesize=_BLOCKSIZE, numberblocks=0, i=[],  0
        data = ""

        for i in range(0,number_blocks) :
            data += self.readBlock(serverStart, i, path)

        if (filesize%_BLOCKSIZE) == 0 :
            data += self.readBlock(serverStart, number_blocks, path)
        else :
            data += (self.readBlock(serverStart, number_blocks, path))[:(filesize%_BLOCKSIZE)]

        return data


    def removexattr(self, path, name):
        attr = self.meta_proxy.removexattr(path, name) # Meta Server
        if attr == _FAILURE :
            pass        # Should return ENOATTR
        return

#    def rename(self, old, new):
  #      for i in data_server_array:
 #           self.data_server_array.rename(old, new) # Data Servers
#
 #       self.meta_proxy.rename(old, new) # Meta
#
#        return

    def rmdir(self, path):
        self.meta_proxy.rmdir(path) # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        return self.meta_proxy.setxattr(path, name, value) # Meta Server

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    """
#    def symlink(self, target, source):
        # Data Servers
        self.meta_proxy.symlink(target, len(source)) # Meta Server

#    def truncate(self, path, length, fh=None):
        self.meta_proxy.truncate(path, length) # Meta Server

        # Data Servers
        startServer = self.startHash(path)
        length = float(length)
        bsize = float(bsize
        keep = length/bsize
        for i in data_server_array:
            self.data_server_array[(startServer+i)%numServers].truncateData(floor(keep))
        if (keep-floor(keep))) > 0
            trunc = self.data_server_arrray[resolveBlkNum(path,floor(keep))].get(path,floor(keep)/numServers)
            for i in len((_BLOCKSIZE-((keep-floor(keep))*_BLOCKSIZE)):
                trunc[7-i] = None
                self.data_server_arrray[resolveBlkNum(path,floor(keep))].putOverwrite(path,trunc,floor(keep)/numServers)         

#    def unlink(self, path):
        self.meta_proxy.unlink(path) # Meta Server
        # Data Servers
        startServer = self.startHash(path)
        #for i in data_proxy_array:
        #    self.data_proxy_array[(startServer+i)%numServers].unlink(path)
    """

    def utimens(self, path, times=None):
        if times :
            self.meta_proxy.utimens(path, times) # Meta Server
        else :
            self.meta_proxy.utimens(path)

    def write(self, path, data, offset, fh):

        # Data Servers
        serverStart0 = self.startHash(path)
        current_filesize = self.meta_proxy.getxattr(path,'st_size')

        blocks_existing = current_filesize / _BLOCKSIZE
        block_offset_start = offset / _BLOCKSIZE

        for serverStart in [serverStart0] :

            # If Block # Offset is Past Current Blocks Existing, Need to Add Null Characters Blocks
            if( blocks_existing < block_offset_start ) :

                # Add Empty Null Character Blocks Up To, But Not Including, Block_Offset_Start
                for i in range(blocks_existing+1, block_offset_start):
                    self.appendBlock( serverStart, i, path, ("/x00"*_BLOCKSIZE) )

                # Add Character Block Starting At Offset
                start_pos = 0
                end_pos = _BLOCKSIZE-(offset%_BLOCKSIZE)
                
                # Special Case When (len(data)) is Less Than What Can Be Written
                if end_pos >= len(data) :
                    self.appendBlock( serverStart, block_offset_start, path,
                        (("/x00"*(offset%_BLOCKSIZE))+data[start_pos:len(data)]+("/x00"*(end_pos-len(data))))
                    )
                    break

                # Else, Add As Normal
                self.appendBlock( serverStart, block_offset_start, path, (("/x00"*(offset%_BLOCKSIZE))+data[start_pos:end_pos]) )
                start_pos = end_pos
                end_pos += _BLOCKSIZE
                current_block_number = block_offset_start+1

                # EG: if end_pos is 10, and len(data) is 10, Does work!
                while end_pos <= len(data) :
                    self.appendBlock( serverStart, current_block_number, path, data[start_pos:end_pos] )
                    start_pos += _BLOCKSIZE
                    end_pos += _BLOCKSIZE
                    current_block_number += 1

                # Add Final Block w/ Null Characters
                if start_pos == len(data) :
                    # If start_pos Is Exactly Equal To The Amount of Existing Data, End
                    break
                else :
                    self.appendBlock(   serverStart, 
                                        current_block_number, 
                                        path, 
                                        ( data[start_pos:len(data)]+((_BLOCKSIZE-(len(data)-start_pos))*"/x00") )
                    )
                    break


            # If Offset Starts Within Current Existing Block
            else :

                current_block = block_offset_start

                start_pos_inBlock = offset%_BLOCKSIZE
                start_pos_inData = 0
                end_pos_inData = _BLOCKSIZE - start_pos_inBlock

                # If Needed, Load and Overwrite In The Middle of a Block
                if start_pos_inBlock != 0 :

                    if end_pos_inData > len(data) : #String(Small) Lies Within Current Block
                        temp_string = self.readBlock( serverStart, block_offset_start, path )
                        temp_string = temp_string[:start_pos_inBlock] + data[:len(data)] + temp_string[start_pos_inBlock+len(data):]
                        self.overwriteBlock( serverStart, block_offset_start, path, temp_string)
                        break

                    temp_string = self.readBlock( serverStart, block_offset_start, path )
                    temp_string = temp_string[:start_pos_inBlock] + data[:end_pos_inData]

                    self.overwriteBlock(    serverStart,
                                            block_offset_start,
                                            path,
                                            temp_string
                    )
                    current_block += 1
                    start_pos_inData = end_pos_inData
                    end_pos_inData += _BLOCKSIZE

                # Overwrite/Append Block
                # Overwrite
                while current_block < blocks_existing :
                    if end_pos_inData <= len(data) :
                        self.overwriteBlock( serverStart, current_block, path, data[start_pos_inData:end_pos_inData] )
                        start_pos_inData += _BLOCKSIZE
                        end_pos_inData += _BLOCKSIZE
                        current_block += 1

                    else :
                        # Deal W/ Uneven Final Block, And End
                        if start_pos_inData >= len(data) :
                            break
                        temp_string = self.readBlock(serverStart, current_block, path)
                        temp_string = data[(start_pos_inData):(len(data))] + temp_string[(len(data)-start_pos_inData):]
                        self.overwriteBlock(serverStart,current_block,path,temp_string)
                        break

                # Append
                # EG: if end_pos is 10, and len(data) is 10, Does work!
                while end_pos_inData <= len(data) :
                    self.appendBlock( serverStart, current_block, path, data[start_pos_inData:end_pos_inData] )
                    start_pos_inData += _BLOCKSIZE
                    end_pos_inData += _BLOCKSIZE
                    current_block += 1

                # Add Final Block w/ Null Characters
                if start_pos_inData == len(data) :
                    # If start_pos Is Exactly Equal To The Amount of Existing Data, End
                    break
                else :
                    self.appendBlock(   serverStart, 
                                        current_block, 
                                        path, 
                                        ( data[start_pos_inData:len(data)]+((_BLOCKSIZE-(len(data)-start_pos_inData))*"/x00") )
                    )
                    break
        self.meta_proxy.write(path, len(data), offset) # Meta Server
        return

                    
def main():

    if( len(sys.argv) < 6 ) :
        print('usage: %s <metaserver port> <dataserver ports)' % sys.argv[0])
        return

    iDataPorts = []
    for i in range(2,len(sys.argv)) :
        iDataPorts.append( int(sys.argv[i]) )

    test = Memory( int(sys.argv[1]), iDataPorts )

    #def write(self, path, data, offset, fh):
    #def readlink(self, path):

    test.create("test.txt", 0)
    test.write("test.txt", "Hello World", 0, 0)
    print(test.readlink("test.txt"))

    return


if __name__ == '__main__':
    main()
