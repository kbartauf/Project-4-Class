import sys
import xmlrpclib
from xmlrpclib import Binary
import random
from string import ascii_letters

_BLOCKSIZE = 8

def main():

    if( len(sys.argv) < 7 ) :
        print('usage: %s <metaserver port> <dataserver ports (x4)> <filename to corrupt>' % sys.argv[0])
        return

    meta_proxy = xmlrpclib.ServerProxy("http://localhost:"+str(sys.argv[1])+"/")

    data_proxy_array = []
    for i in range(2,len(sys.argv)-1) :
        data_proxy_array.append( xmlrpclib.ServerProxy("http://localhost:"+str(sys.argv[i])+"/") )    
    number_data_servers = len(data_proxy_array)

    filename = sys.argv[len(sys.argv)-1]

    # Randomly Selects Starting Server of the 3 Existing Copies
    random_012 = random.randint(0,2) # RANDINT()
    server_start = (hash(filename) + random_012)%number_data_servers

    # Randomly Select Block Number Within File
    st_size = meta_proxy.getxattr(filename,'st_size')
    number_blocks = st_size/_BLOCKSIZE
    if (st_size%_BLOCKSIZE != 0) :
        number_blocks += 1
    random_block = random.randint(0,number_blocks-1) # RANDINT()

    string = data_proxy_array[(server_start+random_block)%number_data_servers].get(    (filename+str(server_start)),
                                                                                            (random_block/number_data_servers) )
    string = string.data #UnBinary

    # "Corrupt"
    character_pos = random.randint(0,_BLOCKSIZE-1)
    random_character = random.choice(ascii_letters)
    string = string[:character_pos]+random_character+string[(character_pos+1):]


    # putOverwrite
    data_proxy_array[(server_start+random_block)%number_data_servers].putOverwrite( (filename+str(server_start)), 
                                                                                     Binary(string), 
                                                                                     random_block/number_data_servers )
    return


if __name__ == '__main__':
    main()
