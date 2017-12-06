import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve
from collections import defaultdict

_SUCCESS = 0
_FAILURE = 1


class dataserver():

    def __init__(self, server_number_string):
        self.shelveString = ""
        self.shelveString += "data store "
        self.shelveString += server_number_string


    # Retrieve something from the HT
    def get(self, key, blkNum):

        hashkey = str(hash(key))
        d = shelve.open(self.shelveString)

        # Default return value
        rv = "" #"/x00"*8
        # If the key is in the data structure, return properly formated results
        if d.has_key(hashkey) :
            temp = d[hashkey]
            rv = temp[blkNum]
            d.close()
            print("get("+hashkey+","+str(blkNum)+"): "+rv)
            return rv
        else :
            d.close()
            print("get _FAILURE")
            return _FAILURE


    def truncateData(self, path, numBlks):

        hashkey = str(hash(path))
        d = shelve.open(self.shelveString)

        temp = d[hashkey]
        temp = temp[:numBlks]
        d[hashkey] = temp 

        d.close()
        print("truncate _SUCCESS")
        return _SUCCESS


    # Insert something into the HT
    def putAppend(self, key, value):

        hashkey = str(hash(key))
        d = shelve.open(self.shelveString)

        if d.has_key(hashkey) :
            temp = d[hashkey]
        else :
            d[hashkey] = []
            temp = d[hashkey]

        temp.append(value)
        d[hashkey] = temp

        d.close()
        print("putAppend("+hashkey+","+value+")")
        return _SUCCESS


    def putOverwrite(self, key, value, blkNum):

        hashkey = str(hash(key))
        d = shelve.open(self.shelveString)

        if d.has_key(hashkey) :
            temp = d[hashkey]
            temp[blkNum] = value
            d[hashkey] = temp     

            d.close()
            print("putOverwrite("+hashkey+","+value+","+str(blkNum)+")")
            return _SUCCESS   
        else :
            d.close()
            print("putOverwite _FAILURE")
            return _FAILURE

        
    def rename(self, keyold, keynew):
    # !!! Will Give Errors, As Block Start Is Different With Different Hash Values

        hashkeyold = str(hash(keyold))
        hashkeynew = str(hash(keynew))
        d = shelve.open(self.shelveString)

        if d.has_key(hashkeyold) :
            if d.has_key(hashkeynew) :
                # keynew already contains data
                d.close()
                print("Rename _FAILURE")
                return _FAILURE
            else :
                d[hashkeynew] = d[hashkeyold]
                del d[hashkeyold]     

                d.close()
                print("Rename _SUCCESS")
                return _SUCCESS
        else :
            # keyold does not exist
            d.close()
            print("Rename _FAILURE")
            return _FAILURE
    

    def unlink(self, key):
        hashkey = str(hash(key))
        d = shelve.open(self.shelveString)

        if d.has_key(hashkey) :
            del d[hashkey]
            d.close()
            print("_SUCCESS")
            return _SUCCESS
        else :
            d.close()
            print("_FAILURE")
            return _FAILURE


def main():
    if( len(sys.argv) < 6 ) :
        print('usage: %s <int # of dataserver> <at least (x4) mountpoints separated by spaces>' % argv[0])
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
    server.register_function(merp.rename,"rename")
    server.register_function(merp.unlink,"unlink")

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
