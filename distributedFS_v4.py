#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

import sys
import xmlrpclib
from xmlrpclib import Binary

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

_SUCCESS = int(0)
_FAILURE = int(-1)

_BLOCKSIZE = int(8)

class Memory(LoggingMixIn, Operations):

    def __init__(self, iMetaPort, iaDataPorts):
        self.meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(iMetaPort)+"/")
        print("xmlrpclib.ServerProxy(\"http://localhost:"+str(iMetaPort)+"/\")")

        self.data_proxy_array = []
        for i in range(0,len(iaDataPorts)) :
            self.data_proxy_array.append( xmlrpclib.ServerProxy("http://localhost:"+str(iaDataPorts[i])+"/") )
            print("xmlrpclib.ServerProxy(\"http://localhost:"+str(iaDataPorts[i])+"/\")")
        self.number_data_servers = int(len(iaDataPorts))

    # Helper Functions #

    def startHash(self, path):
        return (hash(path)%self.number_data_servers)

    def appendBlock(self, block_start, block_number, pathname, string ):
        block_start = int(block_start)
        block_number = int(block_number)
        # Binary
        return self.data_proxy_array[ int((block_start+block_number)%self.number_data_servers) ].putAppend(pathname,Binary(string))

    def overwriteBlock(self, block_start, block_number, pathname, string):
        block_start = int(block_start)
        block_number = int(block_number)
        # Binary
        return self.data_proxy_array[ int((block_start+block_number)%self.number_data_servers) ].putOverwrite(   pathname, 
                                                                                                        Binary(string), 
                                                                                                    block_number/self.number_data_servers)

    def readBlock(self, block_start, block_number, pathname ):
        block_start = int(block_start)
        block_number = int(block_number)
        #print("self.data_proxy_array[")
        #print( (block_start+block_number)%self.number_data_servers )
        #print("].get(")
        #print(pathname)
        #print(block_number/self.number_data_servers)
        #print(");")

        # Test for Corruption, but if # If temp_string == "" or _FAILURE, readlink()
        #self.readlink(pathname[:-1])

        string = ( self.data_proxy_array[int((block_start+block_number)%self.number_data_servers)].get(pathname,int(block_number/self.number_data_servers)) )

        #print(string)
        string = string.data #Un Binary
        return string

    def readRepair(self, block_start, block_number, pathname):
        block_start_int = int(block_start)
        block_number_int = int(block_number)

        serverStart0 = block_start_int
        serverStart1 = (block_start_int+1)%self.number_data_servers
        serverStart2 = (block_start_int+2)%self.number_data_servers

        path0 = pathname + str(serverStart0)
        path1 = pathname + str(serverStart1)
        path2 = pathname + str(serverStart2)

        string0 = ( self.data_proxy_array[int((serverStart0+block_number_int)%self.number_data_servers)].get(path0,int(block_number_int/self.number_data_servers)) )
        string1 = ( self.data_proxy_array[int((serverStart1+block_number_int)%self.number_data_servers)].get(path1,int(block_number_int/self.number_data_servers)) )
        string2 = ( self.data_proxy_array[int((serverStart2+block_number_int)%self.number_data_servers)].get(path2,int(block_number_int/self.number_data_servers)) )

        string0 = string0.data
        string1 = string1.data
        string2 = string2.data
        
        print("LOOK HERE!")
        print(string0)
        print(string1)
        print(string2)

        counter = 0
        # Test To See If Data Server Crash
        if(string0 == _FAILURE or string0 == "") :
            counter += 1
        if(string1 == _FAILURE or string1 == "") :
            counter += 1
        if(string2 == _FAILURE or string2 == "") :
            counter += 1

        if counter == 3 :
            return ""
        if counter == 1 :
            if(string0 == _FAILURE or string0 == "") :
                self.appendBlock(serverStart0, block_number_int, path0, string2 )
                return string2
            if(string1 == _FAILURE or string1 == "") :
                self.appendBlock(serverStart1, block_number_int, path1, string2 )
                return string2
            if(string2 == _FAILURE or string2 == "") :
                self.appendBlock(serverStart2, block_number_int, path2, string0 )
                return string0
            
        # Test to See If Corruption
        if string0 == string1 :
            if string0 != string2 :
                #Corruption In String2
                self.overwriteBlock(serverStart2, block_number_int, path2, string0)
                return string0

        if string0 == string2 :
            if string0 != string1 :
                #Corruption In String1
                self.overwriteBlock(serverStart1, block_number_int, path1, string0)
                return string1

        if string1 == string2 :
            if string0 != string1 :
                #Corruption in String0
                self.overwriteBlock(serverStart0, block_number_int, path0, string1)
                return string2

        return string0


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
        if path == '' or path == '/' :
            return dict(st_mode=(S_IFDIR|0o755), st_nlink=2,
                                st_size=0,
                                st_ctime=time(),
                                st_mtime=time(),
                                st_atime=time() )

        attrs = self.meta_proxy.getattr(path)
        if attrs == _FAILURE :
            raise FuseOSError(ENOENT)
        print(attrs)
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
        size = int(size)
        offset = int(offset)
        """
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
        """
        data = self.readlink(path)
        return data[offset:(offset+size)]


    def readdir(self, path, fh):
        return self.meta_proxy.readdir() # Meta Server

    def readlink(self, path):
        # Data
        filesize = self.meta_proxy.getxattr(path,'st_size')
        if filesize == _FAILURE :
            return "" #return str ?????
        if filesize == 0 :
            return ""

        number_blocks = int((filesize-1)/_BLOCKSIZE)   #EG: Filesize=9, numberblocks=1, i=[0], 1 
        serverStart = self.startHash(path)          #EG: Filesize=_BLOCKSIZE, numberblocks=0, i=[],  0
        data = ""

        for i in range(0,number_blocks) :
            data += self.readRepair(serverStart, i, path)

        if (filesize%_BLOCKSIZE) == 0 :
            data += self.readRepair(serverStart, number_blocks, path)
        else :
            data += (self.readRepair(serverStart, number_blocks, path))[:(filesize%_BLOCKSIZE)]

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
        self.meta_proxy.setxattr(path, name, value) # Meta Server
        return

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):

        self.unlink(target) # First, Delete File If Already Existing

        serverStart0 = self.startHash(target)
        serverStart1 = (serverStart0 + 1)% self.number_data_servers
        serverStart2 = (serverStart0 + 2)% self.number_data_servers
        for server_start in [serverStart0,serverStart1,serverStart2] :
            pathname = target + str(server_start)

            # Data Servers, Add All Blocks
            number_blocks = int(len(source)/_BLOCKSIZE)
            if (len(source)%_BLOCKSIZE) != 0 :
                number_blocks += 1

            for i in range(0,number_blocks-1) :
                self.appendBlock(server_start,i,pathname,source[(_BLOCKSIZE*i):(_BLOCKSIZE*(i+1))])

            final_block = number_blocks-1
            self.appendBlock(server_start,
                            final_block,
                            pathname,
                            ( source[(_BLOCKSIZE*final_block):] + ("\x00"*(_BLOCKSIZE-(final_block%_BLOCKSIZE))) )
            )

        self.meta_proxy.symlink(target, len(source)) # Meta Server


    def truncate(self, path, length, fh=None):
        length = int(length)

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
        serverStart0 = self.startHash(path)
        serverStart1 = (serverStart0 + 1)% self.number_data_servers
        serverStart2 = (serverStart0 + 2)% self.number_data_servers

        # Data Servers
        for proxy in self.data_proxy_array : # Delete Existing File First, Or Should It Throw an Error?
            proxy.unlink(path+str(serverStart0))
            proxy.unlink(path+str(serverStart1))
            proxy.unlink(path+str(serverStart2))

    def utimens(self, path, times=None):
        if times :
            self.meta_proxy.utimens(path, times) # Meta Server
        else :
            self.meta_proxy.utimens(path)

    def write(self, path, data, offset, fh):
        offset = int(offset)

        self.readlink(path) #Read Repair

        # Data Servers
        pathname = path
        serverStart0 = int(self.startHash(path))
        serverStart1 = int((serverStart0 + 1)% self.number_data_servers)
        serverStart2 = int((serverStart0 + 2)% self.number_data_servers)
        current_filesize = int(self.meta_proxy.getxattr(path,'st_size'))

        blocks_existing = int(current_filesize / _BLOCKSIZE)
        remainder = int(current_filesize % _BLOCKSIZE)
        if remainder != 0 :
            blocks_existing += 1


        block_offset_start = int(offset / _BLOCKSIZE)

        for serverStart in [serverStart0,serverStart1,serverStart2]: #,(serverStart0+1),(serverStart0+2)] :
            path = pathname + str(serverStart)

            #print("serverStart= "+str(serverStart))

            #print("blocks_existing= "+str(blocks_existing)+"<="+"block_offset_start= "+str(block_offset_start))
            # If Block # Offset is Past Current Blocks Existing, Need to Add Null Characters Blocks
            if( blocks_existing <= block_offset_start ) :

                # Add Empty Null Character Blocks Up To, But Not Including, Block_Offset_Start
                for i in range(blocks_existing, block_offset_start):
                    #print("i= "+str(i)+" for adding empty null character blocks")
                    self.appendBlock( serverStart, i, path, ('\x00'*_BLOCKSIZE) )

                # Add Character Block Starting At Offset
                start_pos = 0
                end_pos = _BLOCKSIZE-int(offset%_BLOCKSIZE)
                
                # Special Case When (len(data)) is Less Than What Can Be Written
                #print("special case")
                if end_pos >= len(data) :
                    self.appendBlock( serverStart, block_offset_start, path,
                        (("\x00"*int(offset%_BLOCKSIZE))+data[start_pos:len(data)]+("\x00"*(end_pos-len(data))))
                    )
                    # print("continue_1")
                    continue

                # Else, Add As Normal
                #print("append block start")
                self.appendBlock( serverStart, block_offset_start, path, (("\x00"*int(offset%_BLOCKSIZE))+data[start_pos:end_pos]) )
                start_pos = end_pos
                end_pos += _BLOCKSIZE
                current_block_number = block_offset_start+1

                # EG: if end_pos is 10, and len(data) is 10, Does work!
                while end_pos <= len(data) :
                    #print("end_pos= "+str(end_pos)+" continued appending")
                    self.appendBlock( serverStart, current_block_number, path, data[start_pos:end_pos] )
                    start_pos += _BLOCKSIZE
                    end_pos += _BLOCKSIZE
                    current_block_number += 1

                # Add Final Block w/ Null Characters
                # print("add final block maybe")
                if start_pos == len(data) :
                    # If start_pos Is Exactly Equal To The Amount of Existing Data, End
                    #print("continue_2")
                    continue
                else :
                    self.appendBlock(   serverStart, 
                                        current_block_number, 
                                        path, 
                                        ( data[start_pos:len(data)]+((_BLOCKSIZE-(len(data)-start_pos))*"\x00") )
                    )
                    #print("continue_3")
                    continue


            # If Offset Starts Within Current Existing Block
            else :

                current_block = block_offset_start

                start_pos_inBlock = int(offset%_BLOCKSIZE)
                start_pos_inData = 0
                end_pos_inData = _BLOCKSIZE - start_pos_inBlock

                # If Needed, Load and Overwrite In The Middle of a Block
                if start_pos_inBlock != 0 :

                    if end_pos_inData > len(data) : #String(Small) Lies Within Current Block
                        temp_string = self.readBlock( serverStart, block_offset_start, path )
                        temp_string = temp_string[:start_pos_inBlock] + data[:len(data)] + temp_string[start_pos_inBlock+len(data):]
                        self.overwriteBlock( serverStart, block_offset_start, path, temp_string)
                        #print("continue_4")
                        continue

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
                    #print("Current_block="+str(current_block)+" < Blocks_existing="+str(blocks_existing))
                    if end_pos_inData <= len(data) :
                        self.overwriteBlock( serverStart, current_block, path, data[start_pos_inData:end_pos_inData] )
                        start_pos_inData += _BLOCKSIZE
                        end_pos_inData += _BLOCKSIZE
                        current_block += 1

                    else :
                        # Deal W/ Uneven Final Block, And End
                        if start_pos_inData >= len(data) :
                            #print("break_5")
                            break
                        temp_string = self.readBlock(serverStart, current_block, path)
                        temp_string = data[(start_pos_inData):(len(data))] + temp_string[(len(data)-start_pos_inData):]
                        self.overwriteBlock(serverStart,current_block,path,temp_string)
                        #print("break_6")
                        break
                if end_pos_inData > len(data) :
                    continue

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
                    #print("continue_7")
                    continue
                else :
                    self.appendBlock(   serverStart, 
                                        current_block, 
                                        path, 
                                        ( data[start_pos_inData:len(data)]+((_BLOCKSIZE-(len(data)-start_pos_inData))*"\x00") )
                    )
                    #print("continue__BLOCKSIZE")
                    continue
        return self.meta_proxy.write(pathname, len(data), offset) # Meta Server

                    
if __name__ == '__main__':
    if( len(sys.argv) < 6 ) :
        print('usage: %s fusemount <metaserver port> <dataserver ports>' % sys.argv[0])
        exit(0)

    iDataPorts = []
    for i in range(3,len(sys.argv)) :
        iDataPorts.append( int(sys.argv[i]) )

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE( Memory(int(sys.argv[2]),iDataPorts), argv[1], foreground=True)
