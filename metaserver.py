from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve

_SUCCESS = 0
_FAILURE = 1
_DATABASE = "datasource_test0"

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
        for i in range(0,len(pathname)-1):
            if pathname[i] == '/':
                if pathname[:i+1] not in self.sub_directories :
                    self.sub_directories[pathname[:i+1]] = metaTreeNode(content_ID)
                    d = shelve.open(_DATABASE)
                    d[str(content_ID)] = dict(
                                    st_mode=(S_IFDIR|0o755),
                                    st_ctime=time(),
                                    st_mtime=time(),
                                    st_atime=time(),
                                    st_nlink=2
                                    #st_uid,
                                    #st_gid,
                                    #st_size=0 
                                    )
                    d.close()
                    content_ID += 1
                self.sub_directories[pathname[:i+1]].addFileDirectories(pathname[i+1:], content_ID)

        if pathname[-1] == '/' :
            # Add Final Directory
            if pathname in self.sub_directories :
                return content_ID
            self.sub_directories[pathname] = metaTreeNode(content_ID)
            d = shelve.open(_DATABASE)
            d[str(content_ID)] = dict(
                            st_mode=(S_IFDIR|0o755),
                            st_ctime=time(),
                            st_mtime=time(),
                            st_atime=time(),
                            st_nlink=2
                            #st_uid,
                            #st_gid,
                            #st_size=0 )
                            )
            d.close()
            content_ID += 1
            return content_ID
        else :
            # Add File
            if pathname in self.files_content_numbers :
                return content_ID
            self.files_content_numbers[pathname] = content_ID
            d = shelve.open(_DATABASE)
            d[str(content_ID)] = dict(
                            st_mode=(S_IFREG | mode),
                            st_ctime=time(),
                            st_mtime=time(),
                            st_atime=time(),
                            st_nlink=1,
                            #st_uid,
                            #st_gid,
                            st_size=0  )
            d.close()
            content_ID += 1
            return content_ID

    
    def rmdir_iterate()
        # Delete All Files
        for key in self.files_content_numbers :
            ID = str( self.files_content_numbers[key] )
            d = shelve.open(_DATABASE)
            del d[ID]
            d.close()

        # *invocation:* Run Delete All SubDirectories
        for key in self.sub_directories :
            self.sub_directories[key].rmdir_iterate()
            del self.sub_directories[key] # Delete Tree Nodes

        # Delete Current Directory
        ID = str( self.content_number )
        d = shelve.open(_DATABASE)
        del d[ID]
        d.close()



class metaserver():

    def __init__(self):
        self.root = metaTreeNode(0) #(S_IFDIR|0o755),time(),2
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
        
    def updateFileSystem(self):
        d = shelve.open(_DATABASE)
        d["root"] = self
        d.close()


    ### FUSE Functions ###

    def chmod(self, path, mode):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID]
            attributes["st_mode"] &= 0o770000
            attributes["st_mode"] |= mode
            d[ID] = attributes
            d.close()#
            return _SUCCESS
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def chown(self, path, uid, gid):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID]
            attributes["st_uid"] = uid
            attributes["st_gid"] = gid
            d[ID] = attributes
            d.close()#
            return _SUCCESS
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def create(self, path, mode):
        if path[0] == '/' :
            path = path[1:]

        if self.metaserverFindFileOrDirectory(path) != 0 :
            # File Already Exists
            return _FAILURE

        self.addContent(path, self.shelve_integer)
        self.chmod(path, mode)
        self.updateFileSystem()
        return _SUCCESS


    def getattr(self, path):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID]
            d.close()#
            return attributes # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE # Failure


    def getxattr(self, path, name):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            d.close()#
            if name not in attributes
                return 0 # Failure
            return attributes[name] # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE

        
    def listxattr(self, path):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            d.close()#
            return attributes.keys() # Success
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def mkdir(self, path, mode):
        if path[0] == '/' :
            path = path[1:]

        self.addContent(path, self.shelve_integer)
        self.chmod(path, mode)
        self.updateFileSystem()
        return _SUCCESS


    def open(self):
        self.fd += 1
        return self.fd


    def readdir(self):
        # Obtain All File + Directory Names, Excluding The Root '/'
        all_file_directory_paths = []

        stack = []
        working_node = self.root
        stack.append(self.root)

        string_stack = []
        working_string = ""
        string_stack.append("")


        while(len(stack)!=0) :
            working_node = stack.pop()
            working_string = string_stack.pop()

            for key in working_node.files_content_numbers :
                all_file_directory_paths.append(working_string+key)
            
            for key in working_node.sub_directories :
                all_file_directory_paths.append(working_string+key)
                stack.append(working_node.sub_directories[key])
                string_stack.append(working_string+key)

        # return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        return ['.','..'] + [all_file_directory_paths.pop() while len(all_file_directory_paths)>0]


    def removexattr(self, path, name):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            if name not in attributes
                return 0 # Failure
            del attributes[name] 
            d[ID] = attributes
            d.close()
            return _SUCCESS
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def rename(self, old, new):
        # Move DirectoryNode / File
        parent_node = self.root
        current_node = self.root
        element_start = 0

        # Delete Directory, Subdirectories, and Files
        for i in range(0,len(path)-1) :
            if path[i] == '/' :
                if path[element_start:i+1] in current_node.sub_directories :
                    parent_node = current_node
                    current_node = current_node.sub_directories[path[element_start:i+1]]
                    element_start = i+2


    def rmdir(self, path):
        parent_node = self.root
        current_node = self.root
        element_start = 0

        # Delete Directory, Subdirectories, and Files
        for i in range(0,len(path)-1) :
            if path[i] == '/' :
                if path[element_start:i+1] in current_node.sub_directories :
                    parent_node = current_node
                    current_node = current_node.sub_directories[path[element_start:i+1]]
                    element_start = i+2

        # Delete Directories
        if path[element_start:] in current_node.sub_directories :
            current_node.rmdir_iterate()
            del current_node #AHHH So I need to delete it in the original list as, well, will probably cause an error
            return _SUCCESS

        return _FAILURE # No Existing File/Directory
                
                    
    def setxattr(self, path, name, value):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID].get('attrs', {})
            if name not in attributes
                return 0 # Failure
            attributes[name] = value
            d[ID] = attributes
            d.close()#
            return _SUCCESS
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def symlink(self, target, source_len):
        self.addContent(target, self.shelve_integer)
        self.chmod(path, (S_IFLNK | 0o777))
        self.truncate(path, source_len)
        return _SUCCESS


    def truncate(self, path, length):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            # No File or Directory
            self.addContent(path, self.shelve_integer)
            ID = self.metaserverFindFileOrDirectory(path)

        ID = str(ID)
        d = shelve.open(_DATABASE)

        attributes = d[ID]
        attributes["st_size"] = length
        d.close()#
        return attributes["st_size"] # Success


    def unlink(self, path):
        # Delete File, Symbolic Link, Hard Link, Special Node
        current_node = self.root
        element_start = 0

        # Delete Directory, Subdirectories, and Files
        for i in range(0,len(path)-1) :
            if path[i] == '/' :
                if path[element_start:i+1] in current_node.sub_directories :
                    current_node = current_node.sub_directories[path[element_start:i+1]]
                    element_start = i+2

        # Delete File
        if path[element_start:] in current_node.files_content_numbers :
            d = selve.open(_DATABASE)
            ID = str(current_node.files_content_numbers[path[element_start:]])
            del d[ID]
            del current_node.files_content_numbers[path[element_start:]]
            d.close()
            return _SUCCESS

        return _FAILURE


    def utimens(self, path, times):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            return _FAILURE # Error In Locating File or Directory

        ID = str(ID)
        d = shelve.open(_DATABASE)
        if d.has_key(ID) :
            attributes = d[ID]
            now = time()
            atime, mtime = times if times else (now, now)

            attributes["st_atime"] = atime
            attributes["st_mtime"] = mtime
            d[ID] = attributes
            d.close()#
            return _SUCCESS
        else :
            # ERROR IN LOCATING
            d.close()#
            return _FAILURE


    def write(self, path, length, offset):
        ID = self.metaserverFindFileOrDirectory(path)
        if ID == 0 :
            # No File or Directory
            self.addContent(path, self.shelve_integer)
            ID = self.metaserverFindFileOrDirectory(path)

        ID = str(ID)
        d = shelve.open(_DATABASE)

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
    d = shelve.open(_DATABASE)
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
    server.register_function(merp.chown,"chown")
    server.register_function(merp.create,"create")
    server.register_function(merp.getattr,"getattr")
    server.register_function(merp.getxattr,"getxattr")
    server.register_function(merp.listxattr,"listxattr")
    server.register_function(merp.mkdir,"mkdir")
    server.register_function(merp.open,"open")
    server.register_function(merp.readdir,"readdir")
    server.register_function(merp.removexattr,"removexattr")
    server.register_function(merp.rename,"rename")
    server.register_function(merp.rmdir,"rmdir")
    server.register_function(merp.setxattr,"setxattr")
    server.register_function(merp.symlink,"symlink")
    server.register_function(merp.truncate,"truncate")
    server.register_function(merp.unlink,"unlink")
    server.register_function(merp.utimens,"utimens")
    server.register_function(merp.write,"write")

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
