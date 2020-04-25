from ecoms import EasyCommunicationMaster
from sys import argv

port = int(argv[1])

master = EasyCommunicationMaster(port, slave_ip="localhost")
while True:
    data = master.wait_until_receiving()
    master.send(**data)
