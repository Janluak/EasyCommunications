import socket, logging, time
from pickle import dumps, loads, UnpicklingError
from select import select


class EasyCommunicationElement:
    def __init__(self, statusCode=None, payload=None, error=None, **kwargs):
        if statusCode:
            self.statusCode = statusCode
        if payload:
            self.payload = payload
        if error:
            self.error = error
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)

    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def keys(self):
        return self.__dict__.keys()


class EasyCommunicationHandler:
    def __init__(self, host, communication_object=None):
        if host in ["localhost", "127.0.0.1"]:
            self.host = socket.gethostname()
        elif not host:
            self.host = ""
        else:
            self.host = host

        if not communication_object:
            communication_object = EasyCommunicationElement
        self.communication_object = communication_object

        self._connection = socket.socket()

    def send(self, statusCode=None, payload=None, error=None, **kwargs):
        data = self.communication_object(
            statusCode=statusCode, payload=payload, error=error, **kwargs
        )
        logging.debug(f"sending data: {data}")
        data = dumps(data)
        self._connection.send(data)

    def receive(self):
        """
        If data on connection, returns parsed data.
        Else False

        Returns
        -------
        data : bool, any

        """
        ready_to_read, ready_to_write, in_error = select(
            [self._connection], [self._connection], [self._connection], 10
        )
        if ready_to_read:
            try:
                data = self._connection.recv(1024)
            except ConnectionResetError:
                print("ws shut down")  # ToDo
                raise SystemExit
        else:
            return False
        if data:
            try:
                data = loads(data)
                return data
            except UnpicklingError:
                raise ValueError

    def wait_until_receiving(self, timeout=None):
        data = False
        timestamp = time.time()

        # loop until data
        while isinstance(timeout, type(None)) or timestamp + timeout > time.time():
            data = self.receive()
            if data:
                return data
        else:
            raise TimeoutError


class EasyCommunicationSlave(EasyCommunicationHandler):
    def __init__(self, host, port, service_name=None):
        super().__init__(host)

        self.__connect_to_master(port, service_name)

    def __connect_to_master(self, port, service_name):
        self._connection.connect((self.host, port))
        self.send(
            request="INIT",
            payload={"serviceName": service_name if service_name else "unknown"},
        )
        data = self.wait_until_receiving()

        if data.statusCode == 200:
            logging.log(25, f"successfully connected to master {self.host}:{port}")
        else:
            # ToDo Error handling
            raise IOError("cant connect to socket")


class EasyCommunicationMaster(EasyCommunicationHandler):
    def __init__(self, port, slave_ip=None):
        super().__init__(slave_ip)
        if self.host == socket.gethostname():
            logging.warning("only accepting local connections")
        else:
            logging.warning("accepting connections from all IPs")
        self.__open_port_for_slave(port)

    def __open_port_for_slave(self, port):
        while True:
            self._connection.bind((self.host, port))
            self._connection.listen(2)
            logging.info(f"master listening on port {port}")

            self._connection, addr = self._connection.accept()
            data = self.wait_until_receiving()
            if data.request == "INIT":
                logging.log(
                    25,
                    f"Control connection for {data.payload['serviceName']} from {addr[0]}:{addr[1]} to port {port} established",
                )
                self.send(statusCode=200)
                return
            else:
                logging.error(
                    f"Control connection for {data.payload['serviceName']} failed from from {addr[0]}:{addr[1]} to port {port}"
                )
                self.send(statusCode=404)
                raise ConnectionError
