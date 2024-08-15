
from os import access
import socket
from debugger import logger
import time
from protocolSwitcher import CLOSE_CONN, FILE_FIN, FILE_SEND, FILE_START, FILE_SYNC, RESEND


class socketModule(object):

    DECODING = "utf-8"
    ENCODING = "utf-8"
    MAX_DATA = 1024
    MAX_CLIENTS = 10


    """
    """
    def __init__(self):

        self.default_timeout = socket.getdefaulttimeout()
        self.last_sent_packet = None
        pass


    """
    """
    def createSocket(self, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock


    """
    """
    def reply(self, data, connection):

        if isinstance(data, bytes) is False:
            data = data.encode(self.ENCODING)
        
        self.last_sent_packet = data
        connection.send(data)
        logger("--> DATA: {}".format(data))
 


    """
    """
    def read(self, connection, attempt=0):
        try:
            connection.settimeout(5)
            data = connection.recv(self.MAX_DATA)
            logger("<-- DATA: {}".format(data))
            return data
        except Exception as e:
            if(attempt < 3):
                #self.reply(self.last_sent_packet, connection)
                attempt += 1
                return self.read(connection, attempt) # check return
            else:
                logger("TIMEOUT ERROR - MAX ATTEMPTS REACHED!")
                logger(e)
                return ""

    """
    """
    def acceptConnection(self, server, connection, address):

        logger("Got connection {} from: {}".format(connection, address))
        connection.settimeout(5)
        while True:

            try:
                data = self.read(connection)
                if(len(data) > 1):
                    server.handleInput(data, connection)
                
                if(len(data) == 0):
                    break

            except Exception as e:

                logger("{}".format(e))

                connection.close()
                server.cleanUpConnections()

                break




    def create_server(self, **kwargs):

        PORT = int(kwargs["PORT"])
        IP = kwargs["IP"]
        Server = kwargs["SERVER"]
        address = (IP, PORT)

        try:
            with self.createSocket() as s:
                s.bind( address )
                s.listen(self.MAX_CLIENTS)
                logger("Created server {}".format(s))
                while True:
                    conn, addr = s.accept()
                    Server.connected_clients.append(Server.executor.submit( self.acceptConnection, Server, conn, addr))
        except Exception as e:
            logger("{}".format(e))
            
