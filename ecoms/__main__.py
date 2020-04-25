from ecoms import EasyCommunicationSlave
from ast import literal_eval
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host", nargs=1)
parser.add_argument("port", nargs=1, type=int)
parser.add_argument("payload", nargs='*')
data = parser.parse_args()

host = data.host[0]
port = data.port[0]

try:
    payload = literal_eval(bytes.fromhex(data.payload[0]).decode("utf-8"))
except SyntaxError:
    payload = bytes.fromhex(data.payload[0]).decode("utf-8")
except Exception as e:
    payload = " ".join(data.payload)
if not payload:
    raise KeyError("host, port and payload must be given")

while True:
    try:
        slave = EasyCommunicationSlave(host=host, port=port)
        break
    except ConnectionRefusedError:
        pass
slave.send(payload=payload)
data = slave.wait_until_receiving()
slave.close_connection()
