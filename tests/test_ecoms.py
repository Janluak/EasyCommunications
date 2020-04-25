from unittest import TestCase
from subprocess import Popen
import time
from ecoms import *

master_port = 8659


class TestEcomsWithMaster(TestCase):
    def setUp(self) -> None:
        self.echo_master = Popen(f"python3 echo_master.py {master_port}", shell=True)
        time.sleep(0.5)

    def tearDown(self) -> None:
        self.echo_master.kill()
        time.sleep(0.5)

    def test_echo(self):
        payload = {"someKey": "Something"}

        slave = EasyCommunicationSlave(host="localhost", port=master_port)
        slave.send(payload=payload)
        data = slave.wait_until_receiving(timeout=2)

        self.assertEqual(payload, data.payload)


class TestEcomsWithSlave(TestCase):
    def setUp(self) -> None:
        self.data = "someData"
        self.echo_slave = Popen(f"python3 echo_slave.py {master_port} {str(self.data)}", shell=True)
        self.master = EasyCommunicationMaster(master_port, slave_ip="localhost")
        time.sleep(0.5)

    def tearDown(self) -> None:
        self.echo_slave.kill()
        time.sleep(0.5)

    def test_echo(self):
        received = self.master.wait_until_receiving(timeout=2)
        self.assertEqual(self.data, received.payload)
