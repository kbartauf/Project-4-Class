from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve
from collections import defaultdict


class dataserver():

    def __init__(self):
        self.dataServerShelve = shelve.open("data store" + [serverNum])
        self.files = {}
        self.data = defaultdict(list)

    # Retrieve something from the HT
    def get(self, key, blkNum):
        # Default return value
        rv = {}
        # If the key is in the data structure, return properly formated results
        key = key.data
        if key in self.data:
            rv = dataServerShelve[str(hash(path))][blkNum]
        return rv

    def truncateData(lengthBlks):
       temp = dataServerShelve[str(hash(path))]
       temp = temp[:lengthBlks+1]
       dataServerShelve[str(hash(path))] = temp 

    # Insert something into the HT
    def putAppend(self, key, value):
        if dataServerShelve.has_key(key)
            dataServerShelve[str(hash(path))].append(value)
        else
            mklist(key)
            dataServerShelve[str(hash(path))].append(value)

    def putOverwirte(self, key, value, blkNum):
       temp = dataServerShelve[str(hash(path))]
       temp[blkNum] = value
       dataServerShelve[str(hash(path))] = temp        

    def mklist(key):
        dataServerShelve[str(hash(key))] = []
        
    def rename(keyold, keynew)
        dataServerShelve[str(hash(keynew))] = dataServerShelve[str(hash(keyold))]
        del dataServerShelve[str(hash(keyold))]     
    
    def unlink(key)
        del dataServerShelve[str(hash(key))]
#YO
def main():
    if( len(sys.argv) < 6 )
        print('usage: %s <int #dataservers> <at least (x4) mountpoints separated by spaces>' % argv[0])
    iPortNumber = int(sys.argv[ int(sys.argv[1])+2 ])

    #Create test_class
    merp = dataserver()

    # Create Server
    server = SimpleXMLRPCServer(("localhost", iPortNumber))
    server.register_introspection_functions()

    # Register Functions
    server.register_function(,"mkdir")
    server.register_function(merp.get,"read")
    server.register_function(,"readlink")
    server.register_function(,"rename")
    server.register_function(,"rmdir")
    server.register_function(,"symlink")
    server.register_function(,"truncate")
    server.register_function(,"unlink")
    server.register_function(,"write")

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
