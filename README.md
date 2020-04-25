# EasyCommunications (EComs): easy handling of communication between python scripts
This library is a light-weight support for connecting different python scripts via TCP

## Installation
The minimal required python version is `Python3.6`.
The easiest installation can be done by `pip3 install EasyCommunications`.

## Getting started
Once installed, just import the package by `import ecoms`.
For exchanging data between two endpoints (the scripts), one must be the master and the other one the slave.
The master must open the connection first for the slave to connect to it. Once the scripts are connected, communication is completely bi-directional.

### Master
Initialize the communication and send "abc" as payload to the slave and wait infinitely until answering:<br/>
`master = EasyCommunicationMaster(some_port)`<br/>
`master.send(payload="abc")`<br/>
`data = master.wait_until_receiving()`

### Slave
Initialize the communication and echo received payload "abc":<br/>
`slave = EasyCommunicationSlave(master_ip, master_port)`<br/>
`data = slave.wait_until_receiving()`<br/>
`slave.send(statusCode=200, payload=data.payload)`

### Quickstart tip
In `/tests` there is an example master echoing everything sent to from localhost.<br/>
Just fire it up for testing with `python3 tests/echo_master.py port`.


## Documentation
For further guidance and help look at the [documentation](https://ecoms.readthedocs.io/en/latest/)

## Requests & contribution
If you desire anything changed in the package or need another feature please just create an issue.

I am happy for everybody wanting to contribute. Simplest way is to start writing issues, forking the repository and contacting me ;)


