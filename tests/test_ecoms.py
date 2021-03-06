from unittest import TestCase
from subprocess import Popen
import time
from ecoms import *


class TestEcomsWithMaster(TestCase):
    def setUp(self) -> None:
        self.master_port = find_free_port()
        self.echo_master = Popen(f"python3 echo_master.py {self.master_port}", shell=True)
        time.sleep(0.5)

    def tearDown(self) -> None:
        self.slave.close_connection()
        self.echo_master.kill()
        time.sleep(0.5)

    def test_echo(self):
        payload = {"someKey": "Something"}

        self.slave = EasyCommunicationSlave(host="localhost", port=self.master_port)
        self.slave.send(payload=payload)
        data = self.slave.wait_until_receiving(timeout=2)

        self.assertEqual(payload, data.payload)


class TestEcomsWithSlave(TestCase):
    def setUp(self) -> None:
        self.master_port = find_free_port()
        self.data = "someData"
        self.echo_slave = Popen(f"python3 echo_slave.py {self.master_port} {str(self.data)}", shell=True)
        self.master = EasyCommunicationMaster(self.master_port, slave_ip="localhost")
        time.sleep(0.5)

    def tearDown(self) -> None:
        self.master.close_connection()
        self.echo_slave.kill()
        time.sleep(0.5)

    def test_echo(self):
        received = self.master.wait_until_receiving(timeout=2)
        self.assertEqual(self.data, received.payload)


class TestEcomsFromShell(TestCase):
    def setUp(self) -> None:
        self.master_port = find_free_port()
        self.payload = "basic strings"
        self.echo_slave = Popen(f"python3 -m ecoms localhost {self.master_port} {self.payload}", shell=True)
        self.master = EasyCommunicationMaster(self.master_port, slave_ip="localhost")

    def tearDown(self) -> None:
        self.master.close_connection()

    def test_1(self):
        received = self.master.wait_until_receiving()

        self.master.send(statusCode=200)
        self.assertEqual(self.payload, received.payload)


class TestEcomsShellDropData(TestCase):
    def do_testing(self):
        self.port = drop_slave_providing_data("localhost", 0, self.payload)
        self.master = EasyCommunicationMaster(port=self.port, slave_ip="localhost")

        received = self.master.wait_until_receiving()
        self.master.send(statusCode=200)

        self.assertEqual(self.payload, received.payload)

    def tearDown(self) -> None:
        self.master.close_connection()

    def test_get_int_from_drop_slave(self):
        self.payload = 3234

        self.do_testing()

    def test_get_float_from_drop_slave(self):
        self.payload = 0.23

        self.do_testing()

    def test_get_string_from_drop_slave(self):
        self.payload = "adsklfjh asdf n"

        self.do_testing()

    def test_get_list_from_drop_slave(self):
        self.payload = ["some Key", "basic data", 23]

        self.do_testing()

    def test_get_set_from_drop_slave(self):
        self.payload = {"some Key", "basic data", 23}

        self.do_testing()

    def test_get_dict_from_drop_slave(self):
        self.payload = {"some Key": "basic data"}

        self.do_testing()


class TestEcomsNativeShellDropData(TestCase):
    def setUp(self) -> None:

        self.port = find_free_port()
        self.data = "asdf sdfslj"

        Popen(f"python3 -m ecoms localhost {self.port} {self.data}", shell=True)

    def tearDown(self) -> None:
        self.master.close_connection()

    def test_get_int_from_drop_slave(self):

        self.master = EasyCommunicationMaster(port=self.port, slave_ip="localhost")
        received = self.master.wait_until_receiving()
        self.master.send(statusCode=200)

        self.assertEqual(self.data, received.payload)
