import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

_SUCCESS = 0
_FAILURE = 1

# To Do:
    # Update nlink Mechanics (Hard Links??)

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

    def getParentDirectory(self, path) :
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


    def createParentDirectory(self, path) :
        pathname = path
        if pathname[0]=='/' :
            pathname = pathname[1:]
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

        return parent_node


    def getName(self, path) :
        
        for i in range(0,len(path)-1) :
            if path[i] == '/' :
                pathname = path[i+1:]
        return pathname


    # Return _FAILURE If An Inappropriate Name Is Given
    def namingShenanigans(self, name):
        # return _FAILURE 
        return _SUCCESS


    ### FUSE Functions ###

    def chmod(self, path, mode):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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

        parent_node = self.createParentDirectory(path)
        pathname = self.getName(path)

        if pathname[-1] == '/' :
            # Directory
            if pathname in parent_node.sub_directories :
                return _FAILURE # Already Exists?
            else :
                parent_node.sub_directories[pathname] = metaTreeNode(self.shelve_integer)
            self.chmod(path, mode)
        else :
            # File
            if pathname in parent_node.files_specs :
                return _FAILURE # Already Exits?
            else :
                parent_node.files_specs[pathname] = dict(
                                                    st_mode=(S_IFREG | mode),
                                                    st_ctime=time(),
                                                    st_mtime=time(),
                                                    st_atime=time(),
                                                    st_nlink=1,
                                                    #st_uid,
                                                    #st_gid,
                                                    st_size=0,
                                                    st_HASH_ID= self.shelve_integer )

        self.shelve_integer += 1
        self.fd += 1
        return self.fd


    def getattr(self, path):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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


    def mkdir(self, path, mode):
        parent_node = self.createParentDirectory(path)
        pathname = self.getName(path)

        if pathname[-1] == '/' :
            # Directory
            if pathname in parent_node.sub_directories :
                return _FAILURE #or _SUCCESS? Already Exists
            else :
                parent_node.sub_directories[pathname] = metaTreeNode(self.shelve_integer)

        return _SUCCESS


    def open(self):
        self.fd += 1
        return self.fd


    def readdir(self):
        # Obtain All File + Directory Names, Excluding The Root '/'
        all_file_directory_paths = []
        stack = []
        string_stack = []

        working_node = self.root
        stack.append(self.root)
        
        working_string = ""
        string_stack.append("")


        while(len(stack)!=0) :
            working_node = stack.pop()
            working_string = string_stack.pop()

            for key in working_node.files_specs :
                all_file_directory_paths.append(working_string+key)
            
            for key in working_node.sub_directories :
                all_file_directory_paths.append(working_string+key)
                stack.append(working_node.sub_directories[key])
                string_stack.append(working_string+key)

        # return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        return ['.','..'] + all_file_directory_paths


    def removexattr(self, path, name):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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


    def rename(self, old, new):
        # If new name is the same as old, return error
        if old == new :
            return _FAILURE

        # If new name already exists, return error
        potential_parent = self.getParentDirectory(new)
        potential_filename = self.getName(new)
        if potential_parent != _FAILURE :
            if potential_filename[-1] == '/' :
                # Directory
                if potential_filename in potential_parent.sub_directories :
                    return _FAILURE
            else :
                # File
                if potential_filename in potential_parent.files_specs :
                    return _FAILURE

        # If old name does not exist, return error
        old_parent_node = self.getParentDirectory(old)
        old_parent_filename = self.getName(old)
        if old_parent_node == _FAILURE :
            return _FAILURE
        if old_parent_filename[-1] == '/' :
            # Directory
            if old_parent_filename not in old_parent_node.sub_directories :
                return _FAILURE
        else :
            # File
            if old_parent_filename not in old_parent_node.files_specs :
                return _FAILURE

        # Change To New Position, Delete Old
            # old_parent_node = self.getParentDirectory(old)
            # old_parent_filename = self.getName(old)
        parent_node = self.createParentDirectory(new)
        pathname = self.getName(new)

        if old_parent_filename[-1] == '/' :
            # Directory
            if pathname[-1] != '/' :
                pathname += '/'
            parent_node.sub_directories.insert( pathname,
                old_parent_node.sub_directories.pop(old_parent_filename) )
            
        else :
            # File
            while pathname[-1] == '/' :
                pathname = pathname[:-1]
                if len(pathname) == 0 :
                    return _FAILURE
            parent_node.files_specs.insert( pathname,
                old_parent_node.files_specs.pop(old_parent_filename) )

        return _SUCCESS


    def rmdir(self, path):
        # Only Remove Empty Directories

        parent_node = self.root
        current_node = self.root
        current_name = path

        # Find Directory, Subdirectories, and Files
        element_start = 0
        for i in range(0,len(path)) :
            if path[i] == '/' :
                if path[element_start:i+1] in current_node.sub_directories :
                    parent_node = current_node
                    current_node = current_node.sub_directories[path[element_start:i+1]]
                    current_name = path[element_start:]
                    element_start = i+2
                else :
                    return _FAILURE

        # Delete Directory
        if path[-1] == '/' :
            if len(current_node.sub_directories) == 0 :
                if len(current_node.files_specs) == 0 :
                    del parent_node.sub_directories[current_name]
                    return _SUCCESS

        # Delete File (In Retrospect, This is Obviously Unnecessary)
        #if current_name in current_node.files_specs :
        #    del current_node.files_specs[current_name]
        #    return _SUCCESS

        return _FAILURE
                
                    
    def setxattr(self, path, name, value):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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


    def symlink(self, target, source_len):
        parent_node = self.createParentDirectory(target)
        filename = self.getName(target)
        
        if filename in parent_node.files_specs :
            return _FAILURE

        parent_node.files_specs[filename] = dict(st_mode= (S_IFLNK | 0o777),
                                                st_nlink= 1,
                                                st_size= source_len )


    def truncate(self, path, length):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename not in parent_node.files_specs :
            return _FAILURE

        parent_node.files_specs[filename]['st_size'] = length        


    def unlink(self, path):
        parent_node = self.root
        current_node = self.root
        current_name = path

        # Find Directory, Subdirectories, and Files
        element_start = 0
        for i in range(0,len(path)) :
            if path[i] == '/' :
                if path[element_start:i+1] in current_node.sub_directories :
                    parent_node = current_node
                    current_node = current_node.sub_directories[path[element_start:i+1]]
                    current_name = path[element_start:]
                    element_start = i+2
                else :
                    return _FAILURE

        # If Directory, Delete Directories Recursively
        if path[-1] == '/' :

            # Parent Nodes w/ Children to Be Deleted
            node_stack = []
            node_stack.append(parent_node)
            string_stack = []
            string_stack.append(current_name)

            # Directory Stack To Iterate Through
            working_node = None
            working_string = ""
            directory_stack = []
            directory_stack.append(current_node)

            # Build Stack With Node Pointers + Names
            while(len(directory_stack)!=0):
                working_node = directory_stack.pop()

                # Delete Files
                for key in working_node.files_specs :
                    del working_node.files_specs[key]

                # Cannot Delete Yet, 
                for key in working_node.sub_directories :
                    # Add To directory_stack to iterate through all lower levels
                    directory_stack.append(working_node)

                    # Create Stacks To Delete All At Once
                    node_stack.append(working_node)
                    string_stack.append(key)

            # Delete Sub Directories Recursively
            while(len(node_stack)!=0) :
                working_node = node_stack.pop()
                working_string = string_stack.pop()
                del working_node.sub_directories[working_string]

            return _SUCCESS


        # If File, Delete File
        if current_name in current_node.files_specs :
            del current_node.files_specs[current_name]
            return _SUCCESS

        return _FAILURE


    def utimens(self, path, times):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

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
                parent_node.files_specs[filename]['st_atime'] = atime
                parent_node.files_specs[filename]['st_mtime'] = mtime
            else :
                return _FAILURE

        return _SUCCESS


    def write(self, path, length, offset):
        parent_node = self.getParentDirectory(path)
        filename = self.getName(path)

        if parent_node == _FAILURE :
            return _FAILURE
        if filename[-1] != '/' :
            # File
            if filename in parent_node.files_specs :
                # If New Data And Offset Are Larger Than Current Size
                if (offset+length) > parent_node.files_specs[filename]['st_size'] :
                    parent_node.files_specs[filename]['st_size'] = (offset+length)
            else :
                # File Does Not Currently Exist
                parent_node.files_specs[filename] = dict(
                                                    st_mode=(S_IFREG|0o777),
                                                    st_ctime=time(),
                                                    st_mtime=time(),
                                                    st_atime=time(),
                                                    st_nlink=1,
                                                    #st_uid,
                                                    #st_gid,
                                                    st_size=length+offset,
                                                    st_HASH_ID= self.shelve_integer )
                self.shelve_integer += 1
            return parent_node.files_specs[filename]['st_size']
        else :
            # Directory
            return _FAILURE
        
        return _FAILURE



def main():
    if( len(sys.argv) != 2 ) :
        print('usage: %s <mountpoint>' % sys.argv[0])
        return _FAILURE
    iPortNumber = int(sys.argv[1])

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
