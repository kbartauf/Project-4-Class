from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve

self.attributes = dict(st_mode=mode,st_ctime=now,st_mtime=now,st_atime=now,st_nlink=nlink)

class metaTreeNode():
# metaTreeNodes are directories
    # metaTreeNodes contain an array of 'files'
    # metaTreeNodes contain an array of 'directories,' or more metaTreeNodes
# each 'file' and 'directory' is associated with a unique content_ID number
    # unique 'directory' IDs can be found in each metaTreeNode
    # unique 'file' IDs can be found in the 'file' array
        # the filename is they key, and the content_ID is the value pair
# each content ID can be used to obtain the stored attributes of the file/directory

    def __init__(self, content_ID, mode, now, nlink):
        self.content_number = content_ID
        self.sub_directories = dict()
        self.files_content_numbers = dict()


    def getContentID(self, pathname):

        for i in range(0,len(pathname)-1): #Iterate Through All But Last Element (Therefore, Characters Within This Range Will Only Include '/' If The Desired File/Directory Is In Another)
            if pathname[i] == '/' :
                if pathname[:i+1] in self.sub_directories :
                    return self.sub_directoreis[pathname[:i+1]].findFileOrDirectory(pathname[i+1:])
                else :
                    return 0 # No Parent Directory Exists
        
        if pathname[-1] == '/' :
        # If Last Character is '/' DIRECTORY
            if pathname in self.sub_directories :
                return self.sub_directories[pathname].content_number
        else :
        # FILE
            if pathname in self.files
                return self.files_content_numbers[pathname]

        return 0 # No File Or Directory With Pathname Exists


    def addFileDirectories(pathname, contentID):
        content_ID = contentID
        for in range(0,len(pathname)-1):
            if pathname[i] == '/':
                if pathname[:i+1] not in self.sub_directories :
                    self.sub_directories[pathname[:i+1]] = metaTreeNode(content_ID, mode, now, nlink)
                    content_ID += 1
                self.sub_directories[pathname[:i+1]].addFileDirectories(pathname[i+1:], content_ID)

        if pathname[-1] == '/' :
            # Add Final Directory
            if pathname in self.sub_directories :
                return content_ID
            self.sub_directories[pathname] = metaTreeNode(content_ID, mode, now, nlink)
            content_ID += 1
            return content_ID
        else :
            # Add File
            if pathname in self.files_content_numbers :
                return content_ID
            self.files_content_numbers[pathname] = content_ID
            content_ID += 1
            return content_ID


class metaserver():

    def __init__(self):
        self.root = metaTreeNode( 0,(S_IFDIR|0o755),time(),2 )
        self.shelve_integer = 1
        self.fd = 0


    def metaserverFindFileOrDirectory(self, pathname):
        if pathname[0] == '/':
            pathname = pathname[1:]
        # Check Function To See If Works!!!
            # Pathname = '/'
            # Pathname = Pathname[1:]
            # Pathname = ???

        if len(pathname) == 0 :
            return 0 # No One Should Edit Root Directory

        return self.root.getContentID(pathname)


    def addContentID(self, pathname):
        # Unique 'shelve_integer' is updated depending on how many new directories and file are added.
        self.shelve_integer = self.root.addFileDirectories(pathname, self.shelve_integer)        
        

    def chmod(self, path, mode):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID]
            attributes["st_mode"] &= 0o770000
            attributes["st_mode"] |= mode
            d[ID] = attributes
            d.close()#
            return 1 # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure


    def chown(self, path, uid, gid):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID]
            attributes["st_uid"] = uid
            attributes["st_gid"] = gid
            d[ID] = attributes
            d.close()#
            return 1 # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def create(self, path, mode):
        if self.metaserverFindFileOrDirectory(path) == 0 :
            return 0 # Failure

        self.addContent(path, self.shelve_integer)
        self.chmod(path, mode)
        return 1 # Success

    def getattr(self, path, fh=None):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID]
            d.close()#
            return attributes # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def getxattr(self, path, name, position=0):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            d.close()#
            if name not in attributes
                return 0 # Failure
            return attributes[name] # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure
        
    def listxattr(self, path):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            d.close()#
            return attributes.keys() # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def mkdir(self, path, mode):
        self.addContent(path, self.shelve_integer)
        self.chmod(path, mode)

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def readdir(self, path, fh):
        # return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        return ['.', '..'] + # Iterated Through All Files And Directories, return w/ complete pathnames

    def removexattr(self, path, name):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            if name not in attributes
                return 0 # Failure
            del attributes[name] 
            d[ID] = attributes
            d.close()
            return 1 # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def rename(self, old, new):
        # Move DirectoryNode / File

    def rmdir(self, path):
        # Delete Directory, Subdirectories, and Files

    def setxattr(self, path, name, value, options, position=0):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            if name not in attributes
                return 0 # Failure
            attributes[name] = value
            d[ID] = attributes
            d.close()#
            return 1 # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def symlink(self, target, source_len):
        self.addContent(target, self.shelve_integer)
        self.chmod(path, (S_IFLNK | 0o777))
        self.truncate(path, source_len)

    def truncate(self, path, length):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            # No File or Directory
            self.addContent(path, self.shelve_integer)
            ID = self.metaserverFindFileOrDirectory(path)

        ID = str(ID)
        d = shelve.open("datasource")

        attributes = d[ID]
        attributes["st_size"] = length
        d.close()#
        return attributes["st_size"] # Success

    def unlink(self, path):
        # Delete File, Symbolic Link, Hard Link, Special Node

    def utimens(self, path, times=None):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return 0 # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open("datasource")
        if d.has_key(ID) :
            attributes = d[ID]
            now = time()
            atime, mtime = times if times else (now, now)

            attributes["st_atime"] = atime
            attributes["st_mtime"] = mtime
            d[ID] = attributes
            d.close()#
            return 1 # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return 0 # Failure

    def write(self, path, length, offset, fh):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            # No File or Directory
            self.addContent(path, self.shelve_integer)
            ID = self.metaserverFindFileOrDirectory(path)

        ID = str(ID)
        d = shelve.open("datasource")

        attributes = d[ID]
        if (offset + length) < attributes["st_size"] :
            # Offset+Length Extends Beyond attributes["st_size"]
            attributes["st_size"] = length + offset
        # else :
            # New Data Offset+Length Does Not Extend Beyond Current Length
            # attributes["st_size"] is the same size

        d.close()#
        return attributes["st_size"] # Success



def main():
    if( len(sys.argv) != 2 )
        print('usage: %s <mountpoint>' % argv[0])
    iPortNumber = int(argv[1])

    #Create Class If Doesnt Exist, Else Load Class
    d = shelve.open("datasource")
    if d.has_key("root") is False :
        merp = metaserver()
        d["root"] = merp
    else :
        merp = d["root"]
    d.close()

    # Create Server
    server = SimpleXMLRPCServer(("localhost", iPortNumber))
    server.register_introspection_functions()

    # Register Functions
    server.register_function(merp.chmod,"chmod")
    server.register_function(merp.chmod,"chown")
    server.register_function(merp.chmod,"create")
    server.register_function(merp.chmod,"getattr")
    server.register_function(merp.chmod,"getxattr")
    server.register_function(,"listxattr")
    server.register_function(,"mkdir")
    server.register_function(,"open")
    server.register_function(,"readdir")
    server.register_function(,"removexattr")
    server.register_function(,"rename")
    server.register_function(,"rmdir")
    server.register_function(,"setxattr")
    server.register_function(,"symlink")
    server.register_function(,"truncate")
    server.register_function(,"unlink")
    server.register_function(,"utimens")
    server.register_function(,"write")

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
