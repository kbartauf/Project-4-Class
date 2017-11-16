from SimpleXMLRPCServer import SimpleXMLRPCServer


# Class To Be Instantiated, Runs On Server
class test_class:
    def __init__(self):
        self.number = 1
    def return_number(self):
        return self.number
    def inc_number(self):
        self.number += 1
        return 1
    def echo_number(self, num):
        return num


def main():

    #Create test_class
    merp = test_class()

    # Create Server
    server = SimpleXMLRPCServer(("localhost", 1234))
    server.register_introspection_functions()

    # Register Functions
    server.register_function(merp.return_number, 'return_number')
    server.register_function(merp.inc_number, 'inc_number')
    server.register_function(merp.echo_number, 'echo_number')

    # Run Server's Main Loop
    server.serve_forever()


if __name__ == "__main__":
    main()
