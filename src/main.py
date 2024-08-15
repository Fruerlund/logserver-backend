from local_network import socketModule
from protocolSwitcher import protocolSwitcher
from local_filehandler import fHandler
from debugger import logger
import threading
import os
from concurrent.futures import ThreadPoolExecutor, thread


class threadObject(threading.Thread):

    def __init__(self, server, data, connection):

        threading.Thread.__init__(self)
        self.id = os.getpid()
        self.data = data
        self.server = server
        self.connection = connection

    def run(self, *args):
        self.retval = Server.callback(self.server, self.data, self.connection)


class Connection(object):

    def __init__(self, connection, identifier):
        self.connection = connection
        self.identifier = identifier
        
class Server(object): 

    DATABASE_CONNECTED = True
    CAN_USE_MODULE = False
    HAS_NETWORK = True


    """
    """
    def __init__(self):

        logger("Created: {} THREAD: {}".format(self, threading.get_ident())) 

        self.socketModule = socketModule()
        self.dbConnection = None
        self.executor = ThreadPoolExecutor(10)
        self.connected_clients = list()
        self.switcher = protocolSwitcher(self)
        self.fHandler = fHandler(self)


    def __exit__(self):
        pass
        

    """
    """
    def handle_login(self, data):

        return True


    """
    """
    def setup(self):
        logger("{}".format(""))
        if(self.setupDB()):
            if(self.setupNetwork):
                self.CAN_USE_MODULE = True
        

    """
    """
    def setupNetwork(self):
        try:
            HAS_NETWORK = True
        except Exception as e:
            HAS_NETWORK = False


    """
    """
    def setupDB(self):

        logger("{}".format(""))

        try:
            DATABASE_CONNECTED = True
        except Exception as e:
            logger(e)
            DATABASE_CONNECTED = False
            self.dbConnection = None
        return DATABASE_CONNECTED


    """
    """
    def cleanUpConnections(self):
        logger("{}".format(""))
        for future in self.connected_clients:
            if future._state == "FINISHED":
                self.connected_clients.remove(future)


    """
    """
    def startServer(self, **kwargs):
        SERVER = kwargs["SERVER"]
        logger("{}".format(""))
        if(self.CAN_USE_MODULE):
           self.socketModule.create_server(SERVER=SERVER, IP="0.0.0.0", PORT=5556)
   

  
    """
    """
    def callback(self, *args):

        data = args[0]
        connection = args[1]

        logger("Thread: {} | Data: {}".format(threading.get_ident(), data))
        return self.switcher.indirect(data, connection)
 


    """
    """
    def handleInput(self, data, connection):
        
        try:
            t = threadObject(self, data, connection)
            t.start()
            t.join()

        except Exception as e:
            
            logger(e)


def main():

    S = Server()
    S.setup()
    S.startServer(SERVER=S)

main()