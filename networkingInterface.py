import socket


# This class implements the chat protocol
class Interface:

    # Set up a new udp connection using default settings
    def __init__(self):
        self.udp = UdpConnection()


    # configure(newHostAddress, newHostPort)
    # newHostAddress - The host to connect to
    # newHostPort - The port to connect to on the host
    # Configure the udp connection with an address and port
    def configure(self, newHostAddress, newHostPort):
        self.udp.configure(newHostAddress, newHostPort)


    # setTimeout(time)
    # time - the number of seconds before a timeout occurs.  Pass None for no timeout
    # Set a timeout for the udp connection
    def setTimeout(self, time):
        self.udp.socket.settimeout(time)


    # getHost()
    # returns the configured host as a tuple in the form ("host", port)
    def getHost(self):
        return self.udp.host


    # getSocket()
    # returns the socket for the connection
    def getSocket(self):
        return self.udp.socket


    # becomeHost()
    # Bind to a the configured endpoint
    def becomeHost(self):
        return self.udp.bind()


    # connectToHost()
    # Create a socket to connect to the configured endpoint
    def connectToHost(self):
        return self.udp.connect()


    # sendJoin(data, [dest])
    # data -- the username to use
    # dest -- Optional: the endpoint to send to - defaults to None
    # Send a join message
    def sendJoin(self, data, dest=None):
        self.sendPacket("J:", dest, data)


    # sendList([dest])
    # dest -- Optional: the endpoint to send to - defaults to None
    # Sends a list command
    def sendList(self, dest=None):
        self.sendPacket("L:", dest)


    # sendQuit([dest])
    # dest -- Optional: the endpoint to send to - defaults to None
    # Send a quit command
    def sendQuit(self, dest=None):
        self.sendPacket("Q:", dest)


    # sendShutDown(data, [dest])
    # data -- the password to the server
    # dest -- Optional: the endpoint to send to - defaults to None
    # Send a shutdown message
    def sendShutdown(self, data, dest=None):
        self.sendPacket("S:", dest, data)

    # sendMessage(data, [dest])
    # data -- The text message to send
    # dest -- Optional: the endpoint to send to - defaults to None
    # Send a chat message.  Cannot be an empty string
    def sendMessage(self, data, dest=None):
        if (data != ""):
            self.sendPacket("M:", dest, data)


    # sendParticipants(data, [dest])
    # data -- The string containing connected user information
    # dest -- Optional: the endpoint to send to - defaults to None
    # Sends a participants list
    def sendParticipants(self, data, dest=None):
        self.sendPacket("P:", dest, data)


    # sendPacket(type, destination, [data])
    # type -- The command constant for the message
    # dest -- The endpoint to send to - defaults to the configured host if None
    # data -- The body of the message to send - defaults to the empty string
    # Sends a message to a destination, splitting it on newline characters and in 1000 character segments
    def sendPacket(self, type, destination, data=""):

        # Default the destination to the configured host
        if (destination is None):
            destination = self.getHost()

        # Split the message on newline characters
        for message in data.split("\n"):

            # Split the message into 1000 character segments
            for packet in self.splitMessage(message):
                packet = type + packet
                self.udp.sendPacket(destination, packet.replace("\n", ""))


    # splitMessage(message)
    # message -- the message to send
    # Splits the message into segments of 1490 characters
    # returns a list of message segments
    def splitMessage(self, message):
        maxLength = 1490               # The length of a segment
        split = []                     # The returned list
        index = 0                      # The current index in the string
        length = len(message)          # The length of the message

        # Add segments
        while (index + maxLength < length):
            split.append(message[index:index+maxLength])
            index += maxLength

        # Add the last segment
        split.append(message[index:])

        return split


    # recieve()
    # Recieve a udp datagram and return a tuple containing ("command", "message", ("remote host", remotePort))
    def recieve(self):
        buf, remoteEndpoint = self.udp.recieve()
        data = (buf[0:1], buf[2:].strip("\n"), remoteEndpoint)
        return data


    # setConnectivityTest(on)
    # on -- Whether the connection should timeout
    # Sets the timeout to five seconds when on, and None when not
    def setConnectivityTest(self, on):
        if (on):
            self.setTimeout(5)
        else:
            self.setTimeout(None)


    # testSend(message, [dest])
    # message -- The message to attempt to send
    # dest -- Optional: The remote endpoint to send to - defaults to None
    # Attempt to send a message
    # Returns whether or not it was successful
    def testSend(self, message, dest=None):
        success = True
        self.setConnectivityTest(True)

        try:
            self.sendPacket("", dest, message)
        except:
            success = False

        self.setConnectivityTest(False)
        return success


    # testRecieve([pingMessage], [dest])
    # pingMessage -- Optional: a message to generate a response from the server - defaults to None
    # dest -- Optional: The remote endpoint to send to - defaults to None
    # Attempt to recieve a message from the remote endpoint.  Send a ping message to generate a response
    # if one is provided.
    # Return the recieved message or None on failure
    def testRecieve(self, pingMessage=None, dest=None):

        self.setConnectivityTest(True)

        try:
            if (pingMessage is not None):
                self.sendPacket("", dest, pingMessage)
            data = self.recieve()
        except:
            data = None

        self.setConnectivityTest(False)
        return data


# Class to handle udp connections
class UdpConnection:

    # Set up the local endpoint as ("localhost", 13444) and set the buffer size to 1024
    def __init__(self):
        self.bufferSize = 2048
        self.socket = None
        self.configure("localhost", 13444)


    # configure(newHostAddress, newHostPort)
    # newHostAddress -- The address of the endpoint
    # newHostPort -- The port of the endpoint
    # Configure the connection to use the new host configuration
    def configure(self, newHostAddress, newHostPort):
        self.hostAddress = newHostAddress
        self.hostPort = newHostPort
        self.host = (self.hostAddress.replace("localhost", "127.0.0.1"), self.hostPort)


    # bind()
    # Attempt to connect to the configured endpoint and then bind to it
    # Returns True if both were succesful
    def bind(self):
        if (self.connect()):
            try:
                self.socket.bind(self.host)
                return True
            except:
                return False

        else:
            return False


    # connect()
    # Create a socket for connecting to the configured endpoint
    # Returns True if it was succesful
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return True
        except:
            return False


    # sendPacket(destination, data)
    # destination -- The endpoint to send the message to
    # data -- The message to send
    # Sends a message to an endpoint
    def sendPacket(self, destination, data):
        self.socket.sendto(data.encode('utf-8'), destination)


    # recieve()
    # Recieves a message from the endpoint
    # Returns the data and the remote endpoint
    def recieve(self):
        buf, remoteEndpoint = self.socket.recvfrom(self.bufferSize)
        buf = buf.decode('utf-8')
        return buf, remoteEndpoint
