from .EasyCommunicationHandler import find_free_port
from subprocess import Popen


def drop_slave_providing_data(host: str, port: int, data: any) -> int:
    """
    Using ``subprocess.Popen``, this function spawns a slave trying to connect to a master and handover the given data

    Parameters
    ----------
    host : str
        host_ip where the master will be reachable
    port : int
        port_no on which the master will listen to
        if 0: free port will be found
    data : any
        string of `data` must be encodable with hex

    Returns
    -------
    int
        port which was used

    """

    if not port:
        port = find_free_port()

    Popen(f"python3 -m ecoms {host} {port} {str(data).encode('utf-8').hex()}", shell=True)

    return port
