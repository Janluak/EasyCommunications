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
        self.logger = logging.getLogger(self.__class__.__name__)

        # setting host to either the localhost_name of machine, to wild_card or specific IP
        if host in ["localhost", "127.0.0.1"]:
            self.host = socket.gethostname()
        elif not host:
            self.host = ""
        else:
            self.host = host

        # if not a special ECE is specified, use standard
        if not communication_object:
            communication_object = EasyCommunicationElement
        self.communication_object = communication_object

        self._connection = socket.socket()

    def send(self, statusCode=None, payload=None, error=None, **kwargs):
        """
        Send data to the connected entity

        Parameters
        ----------
        statusCode : int, optional
            statusCodes are fairly well known due to HTTP codes. Not required, but maybe helpful for structuring
        payload : any, optional
            any kind of data that shall be transferred
        error : any, str, optional
            helpful special variable for sharing error information
        kwargs : any, optional
            any kind of data may be specified

        """
        data = self.communication_object(
            statusCode=statusCode, payload=payload, error=error, **kwargs
        )
        self.logger.debug(f"sending data: {data}")
        data = dumps(data)
        self._connection.send(data)

    def receive(self):
        """
        Receive data from the connected entity
        `False` if no data available

        Returns
        -------
        bool, object : EasyCommunicationElement
            if no data is available, returns `False`; else returns the received data

        """
        # non-blocking read: checking the state of the socket
        ready_to_read, ready_to_write, in_error = select(
            [self._connection], [self._connection], [self._connection], 10
        )

        # if no data in queue
        if not ready_to_read:
            return False

        # reading data from queue
        try:
            data = self._connection.recv(1024)
        except ConnectionResetError:
            print("ws shut down")  # ToDo
            raise SystemExit

        # unpacking the data
        try:
            data = loads(data)
            return data
        except UnpicklingError:
            raise ValueError

    def wait_until_receiving(self, timeout=None):
        """
        Wait until data was received from the connected entity

        Parameters
        ----------
        timeout : int, optional
            seconds to wait until not waiting anymore -> raises `TimeoutError`

        Returns
        -------
        object: EasyCommunicationElement
            the received data

        """
        timestamp = time.time()

        # loop until data received
        while isinstance(timeout, type(None)) or timestamp + timeout > time.time():
            data = self.receive()
            if data:
                return data
        else:
            raise TimeoutError


class EasyCommunicationSlave(EasyCommunicationHandler):
    def __init__(self, host, port, service_name=None):
        """
        Initializing the slave

        Parameters
        ----------
        host : str ['192.168.0.1', 'localhost', '127.0.0.1']
            the host IP to connect to
        port : int
            the host port to connect to
        service_name : str, optional
            a name identifying the slave at the server
        """
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
            self.logger.log(25, f"successfully connected to master {self.host}:{port}")
        else:
            # ToDo Error handling
            raise IOError("cant connect to socket")


class EasyCommunicationMaster(EasyCommunicationHandler):
    def __init__(self, port, slave_ip=None):
        """
        Initializing the master

        Parameters
        ----------
        port : int
            the port to open for possible slave connections
        slave_ip : str ['192.168.0.1', 'localhost', '127.0.0.1'], optional
            limiting the possible slave-connections to this particular IP
        """
        super().__init__(slave_ip)
        if self.host == socket.gethostname():
            self.logger.warning("only accepting local connections")
        else:
            self.logger.warning("accepting connections from all IPs")

        self.__open_port_for_slave(port)

    def __open_port_for_slave(self, port):
        while True:
            self._connection.bind((self.host, port))
            self._connection.listen(2)

            self.logger.info(f"master listening on port {port}")

            self._connection, addr = self._connection.accept()

            data = self.wait_until_receiving()
            if data.request == "INIT":
                self.logger.log(
                    25,
                    f"Control connection for {data.payload['serviceName']} from {addr[0]}:{addr[1]} to port {port} established",
                )
                self.send(statusCode=200)
                return

            else:
                self.logger.error(
                    f"Control connection for {data.payload['serviceName']} failed from from {addr[0]}:{addr[1]} to port {port}"
                )
                self.send(statusCode=404)
                raise ConnectionError
