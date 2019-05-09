# Import socket lib
import socket
import time

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# retrieve local hostname
local_hostname = socket.gethostname()

# get fully qualified hostname
local_fqdn = socket.getfqdn()

# get the according IP address
ip_address = socket.gethostbyname(local_hostname)

# output hostname, domain name and IP address
print ("working on %s (%s) with %s" % (local_hostname, local_fqdn, ip_address))

# bind the socket to the port 23456
server_address = ('localhost', 8889)  
print ('starting up on %s port %s' % server_address)  
sock.bind(server_address)

# listen for incoming connections (server mode) with one connection at a time
sock.listen(2)
   
while(True):
    print("Connecting to Socket")
    connection,address = sock.accept()
    print("##################### Data streaming Initiated ####################")
    for row in open("streamdata.txt"):
        print(row)
        connection.send(row.encode())
        time.sleep(1)
    print("#####################         End of Data      ####################")
connection.close()
