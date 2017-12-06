import sys
import xmlrpclib
from xmlrpclib import Binary

_SUCCESS = 0
_FAILURE = -1

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
        # Binary
        return self.data_proxy_array[ (block_start+block_number)%self.number_data_servers ].putAppend(pathname,Binary(string))

    def overwriteBlock(self, block_start, block_number, pathname, string):
        # Binary
        return self.data_proxy_array[ (block_start+block_number)%self.number_data_servers ].putOverwrite(   pathname, 
                                                                                                        Binary(string), 
                                                                                                    block_number/self.number_data_servers)

    def readBlock(self, block_start, block_number, pathname ):
        #print("self.data_proxy_array[")
        #print( (block_start+block_number)%self.number_data_servers )
        #print("].get(")
        #print(pathname)
        #print(block_number/self.number_data_servers)
        #print(");")

        string = ( self.data_proxy_array[(block_start+block_number)%self.number_data_servers].get(pathname,(block_number/self.number_data_servers)) )
        #print(string)
        string = string.data #Un Binary
        return string


    #def readRepair(self, serverStart, block_number, pathname ):


    # Memory Functions #

    def chmod(self, path, mode):
        self.meta_proxy.chmod(path, mode) # Meta Server
        return 0

    def chown(self, path, uid, gid):
        self.meta_proxy.chown(path, uid, gid) # Meta Server

    def create(self, path, mode):
        self.meta_proxy.create(path, mode) # Meta Server
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
        serverStart = self.startHash(path)
        filesize = self.meta_proxy.getxattr(path,'st_size')
        data = ""

        number_blocks_dataserver = filesize/_BLOCKSIZE
        if (filesize%_BLOCKSIZE) != 0 :
            number_blocks_dataserver += 1


        start_block = offset/_BLOCKSIZE
        possible_end_block = (offset+size-1)/_BLOCKSIZE

        if possible_end_block < number_blocks_dataserver :
            for i in range(start_block, possible_end_block+1) :
                data += self.readBlock(serverStart, i, path)
            data = data[(offset%_BLOCKSIZE):((size)+(offset%_BLOCKSIZE))]
            return data

        # if possible_end_block >= number_blocks_dataserver :
        else :
            for i in range(start_block, number_blocks_dataserver) :
                data += self.readBlock(serverStart, i, path)
            data = data[offset%_BLOCKSIZE:]
            return data

        return data


    def readdir(self, path, fh):
        return self.meta_proxy.readdir() # Meta Server

    def readlink(self, path):
        # Data
        filesize = self.meta_proxy.getxattr(path,'st_size')
        if filesize == _FAILURE :
            return "" #return str ?????
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

    def rename(self, old, new):
        mode = self.meta_proxy.getxattr(old,'st_mode')
        #print(mode)
        if mode == _FAILURE :
            #print("OLD does not exist")
            return
        #print("OLD exists")
        data = self.readlink(old)

        temp = self.meta_proxy.getxattr(new,'st_mode')
        #print(temp)
        if temp == _FAILURE :
            #print("NEW does not exist")
            self.unlink(old)
            self.create(new, mode)
            self.write(new, data, 0, 0)
            return
        else :
            #print("NEW already exists")
            return

    def rmdir(self, path):
        self.meta_proxy.rmdir(path) # Meta Server

    def setxattr(self, path, name, value, options, position=0):
        return self.meta_proxy.setxattr(path, name, value) # Meta Server

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):

        server_start = self.startHash(target)
        self.unlink(target) # First, Delete File If Already Existing

        # Data Servers, Add All Blocks
        number_blocks = len(source)/_BLOCKSIZE
        if (len(source)%_BLOCKSIZE) != 0 :
            number_blocks += 1

        for i in range(0,number_blocks-1) :
            self.appendBlock(server_start,i,target,source[(_BLOCKSIZE*i):(_BLOCKSIZE*(i+1))])

        final_block = number_blocks-1
        self.appendBlock(server_start,
                        final_block,
                        target,
                        ( source[(_BLOCKSIZE*final_block):] + ("\x00"*(_BLOCKSIZE-(final_block%_BLOCKSIZE))) )
        )

        self.meta_proxy.symlink(target, len(source)) # Meta Server


    def truncate(self, path, length, fh=None):
        string = self.readlink(path)
        mode = self.getxattr(path,'st_mode')
        if length < len(string) :
            # Shorten
            string = string[:length]
        elif length > len(string) :
            # Lengthen
            string = string+((length-len(string))*'\x00')

        self.unlink(path)
        self.create(path,mode)
        self.write(path,string,0,0)


    def unlink(self, path):
        self.meta_proxy.unlink(path) # Meta Server
        # Data Servers
        for proxy in self.data_proxy_array : # Delete Existing File First, Or Should It Throw an Error?
            proxy.unlink(path)

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
        remainder = current_filesize % _BLOCKSIZE
        if remainder != 0 :
            blocks_existing += 1


        block_offset_start = offset / _BLOCKSIZE

        for serverStart in [serverStart0]: #,(serverStart0+1),(serverStart0+2)] :
            print("serverStart= "+str(serverStart))

            print("blocks_existing= "+str(blocks_existing)+"<="+"block_offset_start= "+str(block_offset_start))
            # If Block # Offset is Past Current Blocks Existing, Need to Add Null Characters Blocks
            if( blocks_existing <= block_offset_start ) :

                # Add Empty Null Character Blocks Up To, But Not Including, Block_Offset_Start
                for i in range(blocks_existing, block_offset_start):
                    print("i= "+str(i)+" for adding empty null character blocks")
                    self.appendBlock( serverStart, i, path, ('\x00'*_BLOCKSIZE) )

                # Add Character Block Starting At Offset
                start_pos = 0
                end_pos = _BLOCKSIZE-(offset%_BLOCKSIZE)
                
                # Special Case When (len(data)) is Less Than What Can Be Written
                print("special case")
                if end_pos >= len(data) :
                    self.appendBlock( serverStart, block_offset_start, path,
                        (("\x00"*(offset%_BLOCKSIZE))+data[start_pos:len(data)]+("\x00"*(end_pos-len(data))))
                    )
                    print("break_1")
                    break

                # Else, Add As Normal
                print("append block start")
                self.appendBlock( serverStart, block_offset_start, path, (("\x00"*(offset%_BLOCKSIZE))+data[start_pos:end_pos]) )
                start_pos = end_pos
                end_pos += _BLOCKSIZE
                current_block_number = block_offset_start+1

                # EG: if end_pos is 10, and len(data) is 10, Does work!
                while end_pos <= len(data) :
                    print("end_pos= "+str(end_pos)+" continued appending")
                    self.appendBlock( serverStart, current_block_number, path, data[start_pos:end_pos] )
                    start_pos += _BLOCKSIZE
                    end_pos += _BLOCKSIZE
                    current_block_number += 1

                # Add Final Block w/ Null Characters
                print("add final block maybe")
                if start_pos == len(data) :
                    # If start_pos Is Exactly Equal To The Amount of Existing Data, End
                    print("break_2")
                    break
                else :
                    self.appendBlock(   serverStart, 
                                        current_block_number, 
                                        path, 
                                        ( data[start_pos:len(data)]+((_BLOCKSIZE-(len(data)-start_pos))*"\x00") )
                    )
                    print("break_3")
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
                        print("break_4")
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
                    print("Current_block="+str(current_block)+" < Blocks_existing="+str(blocks_existing))
                    if end_pos_inData <= len(data) :
                        self.overwriteBlock( serverStart, current_block, path, data[start_pos_inData:end_pos_inData] )
                        start_pos_inData += _BLOCKSIZE
                        end_pos_inData += _BLOCKSIZE
                        current_block += 1

                    else :
                        # Deal W/ Uneven Final Block, And End
                        if start_pos_inData >= len(data) :
                            print("break_5")
                            break
                        temp_string = self.readBlock(serverStart, current_block, path)
                        temp_string = data[(start_pos_inData):(len(data))] + temp_string[(len(data)-start_pos_inData):]
                        self.overwriteBlock(serverStart,current_block,path,temp_string)
                        print("break_6")
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
                    print("break_7")
                    break
                else :
                    self.appendBlock(   serverStart, 
                                        current_block, 
                                        path, 
                                        ( data[start_pos_inData:len(data)]+((_BLOCKSIZE-(len(data)-start_pos_inData))*"\x00") )
                    )
                    print("break__BLOCKSIZE")
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
    #def read(self, path, size, offset, fh)
    #def rename(self, old, new)

    """
    test.create("test1.txt",0)
    test.write("test1.txt","Hello World",17,0)
    print(test.readlink("test1.txt"))
    """

    """
    test.create("test2.txt",0)
    test.write("test2.txt","Hello World",_BLOCKSIZE,0)
    test.write("test2.txt","Hello Again",41,0)
    print(test.readlink("test2.txt"))
    """

    """
    test.create("test3.txt",0)
    test.write("test3.txt","Hello World",7,0)
    test.write("test3.txt","Go Away",13,0)
    print("HERE: "+test.readlink("test3.txt"))

    test.create("test5.txt",0)
    test.write("test5.txt","Go Away",13,0)
    test.write("test5.txt","Hello World",7,0)
    print("HERE: "+test.readlink("test5.txt"))
    """

    """
    test.create("test4.txt",0)
    test.write("test4.txt","Hello Again",41,0)
    print(test.readlink("test4.txt"))
    test.write("test4.txt","Hello World",_BLOCKSIZE,0)
    print(test.readlink("test4.txt"))
    """


    """
    test.create("test.txt", 0)
    test.write("test.txt", "Hello World My Name is Brian Dillon", 0, 0)
    print(test.readlink("test.txt"))
    test.write("test.txt", "Hello World My Name is Kevin Barta ", 0, 0)
    print(test.readlink("test.txt"))

    test.unlink("test.txt")
    print(test.readlink("test.txt"))
    """

    """
    test.symlink("path.txt","data   data data data")
    print(test.readlink("path.txt"))
    print(test.readdir(None,None))

    test.rename("path.txt","otherpath.txt")
    print(test.readlink("path.txt"))
    print(test.readlink("otherpath.txt"))
    print(test.readdir(None,None))

    test.symlink("path.txt","data   data data data") #21 Characters

    test.truncate("path.txt",30)
    test.truncate("otherpath.txt",4)
    print(test.readlink("path.txt"))
    print(test.readlink("otherpath.txt"))

    print(test.getattr("path.txt"))
    print(test.getattr("otherpath.txt"))

    print(test.readdir(None,None))
    """

    test.create("alphabet.txt",0) #a=0,i=8,q=16,y=24
    test.write("alphabet.txt","abcdefghijklmnopqrstuvwxyz",0,0)
    print(test.read("alphabet.txt",8,0,0))
    print(test.read("alphabet.txt",1,1,0))
    print(test.read("alphabet.txt",26,0,0))
    print(test.read("alphabet.txt",26,1,0))
    print(test.read("alphabet.txt",15,20,0))
    print(test.read("alphabet.txt",15,9,0))

    return


    """
    test.create("test.txt", 0)
    test.write("test.txt", "Hello World", 0, 0)
    print(test.readlink("test.txt"))

    return
    """


if __name__ == '__main__':
    main()
