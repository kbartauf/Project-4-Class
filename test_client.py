import xmlrpclib


def main():
    # Start Proxy
    proxy = xmlrpclib.ServerProxy("http://localhost:1234/")

    # Call Functions
    print proxy.return_number()
    proxy.inc_number()
    print proxy.return_number()
    print proxy.echo_number(123)


if __name__ == "__main__":
    main()
