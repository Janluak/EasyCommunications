from ecoms import EasyCommunicationSlave
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host", nargs=1)
parser.add_argument("port", nargs=1, type=int)
parser.add_argument("payload", nargs='*')
data = parser.parse_args()

host = data.host[0]
port = data.port[0]
payload = " ".join(data.payload)
if not payload:
    raise KeyError("host, port and payload must be given")


slave = EasyCommunicationSlave(host=host, port=port)
slave.send(payload=payload)
data = slave.wait_until_receiving()
slave.close_connection()
