from ecoms import EasyCommunicationSlave
from sys import argv

port = int(argv[1])
data = argv[2]

slave = EasyCommunicationSlave(host="localhost", port=port)
while True:
    slave.send(payload=data)
