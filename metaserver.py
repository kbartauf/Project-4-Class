from SimpleXMLRPCServer import SimpleXMLRPCServer

_SUCCESS = 0
_FAILURE = 1

class metaTreeNode():
    def __init__(self, uniqueID):
        self.sub_directories = dict()
        self.files_specs = dict()

        self.directory_spec = dict(
                                st_mode=(S_IFDIR|0o755),
                                st_ctime=time(),
                                st_mtime=time(),
                                st_atime=time(),
                                st_nlink=2,
                                #st_uid,
                                #st_gid,
                                #st_size=0,
                                st_HASH_ID = uniqueID )


class metaserver():

    def __init__(self):
        self.root = metaTreeNode(0)
        self.shelve_integer = 1
        self.fd = 0


    ### Support Functions ###        

    def getParentDirectory(path) :
        node = self.root
        pathname = path
        
        for i in range(0,len(path)-1):
            if pathname[i] == '/' :
                if pathname[:i+1] in node.sub_directories :
                    node = node.sub_directories
                    pathname = pathname[i+1:]
                else :
                    return _FAILURE
        return node


    def getName(path) :
        
        for i in range(0,len(path)-1) :
            if path[i] == '/' :
                pathname = path[i+1:]
        return pathname


    ### FUSE Functions ###

    def chmod(self, path, mode):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                parent_node.sub_directories[filename].directory_spec['st_mode'] &= 0o770000
                parent_node.sub_directories[filename].directory_spec['st_mode'] |= mode
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                parent_node.files_specs[filename]['st_mode'] &= 0o770000
                parent_node.files_specs[filename]['st_mode'] |= mode
            else :
                return _FAILURE

        return _SUCCESS


    def chown(self, path, uid, gid):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                parent_node.sub_directories[filename].directory_spec['st_uid'] = uid
                parent_node.sub_directories[filename].directory_spec['st_gid'] = gid
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                parent_node.files_specs[filename]['st_uid'] = uid
                parent_node.files_specs[filename]['st_gid'] = gid
            else :
                return _FAILURE

        return _SUCCESS


    def create(self, path, mode):
        pathname = path
        if pathname[0]=='/' :
            pathname[1:]
        parent_node = self.root

        h = 0
        for i in range(0,len(pathname)-1) :
            if pathname[i] == '/' :
                if pathname[h:i+1] not in parent_node.sub_directories :
                    parent_node.sub_directories[pathname[h:i+1]] = metaTreeNode(self.shelve_integer)
                    self.shelve_integer += 1
                parent_node = parent_node.sub_directories[pathname[h:i+1]]
                h = i+1
        pathname = pathname[h:]

        if pathname[-1] == '/' :
            # Directory
            if pathname in parent_node.sub_directories :
                # return _FAILURE # Already Exists?
            else :
                parent_node.sub_directories[pathname] = metaTreeNode(self.shelve_integer)
        else :
            # File
            if pathname in parent_node.files_specs :
                # return _FAILURE # Already Exits?
            else :
                parent_node.files_specs[pathname] = dict(
                                                    st_mode=(S_IFDIR|0o755),
                                                    st_ctime=time(),
                                                    st_mtime=time(),
                                                    st_atime=time(),
                                                    st_nlink=2
                                                    #st_uid,
                                                    #st_gid,
                                                    st_size=length+offset,
                                                    st_HASH_ID= self.shelve_integer )

        self.shelve_integer += 1
        self.chmod(path, mode)
        self.fd += 1
        return self.fd


    def getattr(self, path):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                return parent_node.sub_directories[filename].directory_spec
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                return parent_node.files_specs[filename]
            else :
                return _FAILURE


    def getxattr(self, path, name):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                attrs = parent_node.sub_directories[filename].directory_spec.get('attrs', {})
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                attrs = parent_node.files_specs[filename].get('attrs', {})
            else :
                return _FAILURE

        if name in attrs :
            return attrs[name]
        
        return _FAILURE

        
    def listxattr(self, path):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                attrs = parent_node.sub_directories[filename].directory_spec.get('attrs', {})
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                attrs = parent_node.files_specs[filename].get('attrs', {})
            else :
                return _FAILURE

        return attrs.keys()


    #def mkdir(self, path, mode):
        if path[0] == '/' :
            path = path[1:]

        self.addContent(path, self.shelve_integer)
        self.chmod(path, mode)
        self.updateFileSystem()
        return _SUCCESS


    def open(self):
        self.fd += 1
        return self.fd


    #def readdir(self):
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
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                attrs = parent_node.sub_directories[filename].directory_spec.get('attrs', {})
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                attrs = parent_node.files_specs[filename].get('attrs', {})
            else :
                return _FAILURE

        del attrs[name]
        return _SUCCESS


    #def rename(self, old, new):
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


    #def rmdir(self, path):
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
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                attrs = parent_node.sub_directories[filename].directory_spec.setdefault('attrs', {})
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
                attrs = parent_node.files_specs[filename].setdefault('attrs', {})
            else :
                return _FAILURE

        attrs[name] = value
        return _SUCCESS


    #def symlink(self, target, source_len):


    #def truncate(self, path, length):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :

            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
            else :
                return _FAILURE


    #def unlink(self, path):
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
        parent_node = getParentDirectory(path)
        filename = getName(path)

        now = time()
        atime, mtime = times if times else (now, now)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] == '/' :
            # Directory
            if filename in parent_node.sub_directories :
                parent_node.sub_directories[filename].directory_spec['st_atime'] = atime
                parent_node.sub_directories[filename].directory_spec['st_mtime'] = mtime
            else :
                return _FAILURE
        else :
            # File
            if filename in parent_node.files_specs :
            else :
                return _FAILURE

        return _SUCCESS


    def write(self, path, length, offset):
        parent_node = getParentDirectory(path)
        filename = getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] != '/' :
            # File
            if filename in parent_node.files_specs :
                # If New Data And Offset Are Larger Than Current Size
                if (offset+length) > parent_node.files_specs[filename]['st_size']
                    parent_node.files_specs[filename]['st_size'] = (offset+length)
            else :
                # File Does Not Currently Exist
                parent_node.files_specs[filename] = dict(
                                                    st_mode=(S_IFDIR|0o755),
                                                    st_ctime=time(),
                                                    st_mtime=time(),
                                                    st_atime=time(),
                                                    st_nlink=2
                                                    #st_uid,
                                                    #st_gid,
                                                    st_size=length+offset,
                                                    st_HASH_ID= self.shelve_integer )
                self.shelve_integer += 1
            return parent_node.files_specs[filename]['st_size']
        else :
            # Directory
        
        return _FAILURE



def main():
    if( len(sys.argv) != 2 )
        print('usage: %s <mountpoint>' % argv[0])
    iPortNumber = int(argv[1])

    # Create Memory Class
    merp = metaserver()

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
