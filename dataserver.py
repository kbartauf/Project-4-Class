from SimpleXMLRPCServer import SimpleXMLRPCServer
import shelve


class dataserver():

    def __init__(self):


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
    server.register_function(,"read")
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
