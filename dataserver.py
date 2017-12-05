from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve
from collections import defaultdict
import sys
import xmlrpclib


class dataserver():

    def __init__(self, server_number_string):
        self.dataServerShelve = shelve.open("data store " + server_number_string)

    # Retrieve something from the HT
    def get(self, key, blkNum):
        # Default return value
        rv = {}
        # If the key is in the data structure, return properly formated results
        key = key.data
        if dataServerShelve.has_key(key) :
            rv = dataServerShelve[str(hash(path))][blkNum]
        return rv

    def truncateData(self, lengthBlks):
        temp = dataServerShelve[str(hash(path))]
        temp = temp[:lengthBlks+1]
        dataServerShelve[str(hash(path))] = temp 

    # Insert something into the HT
    def putAppend(self, key, value):
        if dataServerShelve.has_key(key):
            dataServerShelve[str(hash(path))].append(value)
        else:
            mklist(key)
            dataServerShelve[str(hash(path))].append(value)

    def putOverwrite(self, key, value, blkNum):
        temp = dataServerShelve[str(hash(path))]
        temp[blkNum] = value
        dataServerShelve[str(hash(path))] = temp        

    def mklist(self, key):
        dataServerShelve[str(hash(key))] = []
        
    def rename(self, keyold, keynew):
        dataServerShelve[str(hash(keynew))] = dataServerShelve[str(hash(keyold))]
        del dataServerShelve[str(hash(keyold))]     
    
    def unlink(self, key):
        del dataServerShelve[str(hash(key))]

def main():
    if( len(sys.argv) < 6 ):
        print('usage: %s <int # of dataserver> <at least (x4) mountpoints separated by spaces>')# % argv[0])
        return
    
    iPortNumber = int(sys.argv[ int(sys.argv[1])+2 ])

    #Create test_class
    merp = dataserver( sys.argv[1] )

    # Create Server
    server = SimpleXMLRPCServer(("localhost", iPortNumber))
    server.register_introspection_functions()

    # Register Functions
    server.register_function(merp.get,"get")
    server.register_function(merp.truncateData,"truncate")
    server.register_function(merp.putAppend,"putAppend")
    server.register_function(merp.putOverwrite,"putOverwrite")
    server.register_function(merp.mklist,"mklist")
    server.register_function(merp.rename,"rename")
    server.register_function(merp.unlink,"unlink")

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
