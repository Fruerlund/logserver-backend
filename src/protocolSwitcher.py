from ast import Bytes
from debugger import logger
import os

ACKW        = b"ACKW"
CONN        = b"CONNECT"
RDY         = b"READY"
ACCP        = b"ACCEPT"
RECJ        = b"REJC"
ERRO        = b"ERROR"
FILE_SEND   = b"FILESEND"
FILE_FIN    = b"FILEFIN"
FILE_START  = b"FILESTART"
FILE_SYNC   = b"FILESYNC"
CLOSE_CONN  = b"CLOSE"
RESEND      = b"RESEND"       
TERM        = b"TERM"
MAX_TRANSFER = 128

class protocolSwitcher(object):

    def __init__(self, server):
        self.server = server
        self.authorized_users = {}


    def indirect(self, index, connection):

        method_name = "handle_" + index.decode("utf-8").replace("\n","")
        try:
            method = getattr(self, method_name)
            return method(connection)
        except Exception as e:
            logger(e)
            return self.not_found(method_name, connection)


    def not_found(self, method, connection):
        logger("Snitch Handler not found for: {}".format(method))
        self.sendACKW(connection)
        pass


    """
    """
    def handle_login(self, identifier):

#        if self.server.handle_login(identifier):

 #           self.authorized_users[connection] = identifier
        return True


    """
    """
    def sendACKW(self, connection):
        self.server.socketModule.reply(ACKW, connection)


    """
    """
    def checkACKW(self, connection):
        data = self.server.socketModule.read(connection)
        if data == ACKW:
            return True
        else:
            return False

    """
    """
    def sendERRO(self, connection):
        self.server.socketModule.reply(ERRO, connection)


    """
    """
    def protocolCompare(self, p1, p2):
        if (p1 == p2):
            return True
        else:
            return False


    """
    
    APP         | SERVER
    CONNECT
                    ACKW
                    READY
    IDENTIFIER      
                    ACKW
                    ACCEPT OR REJECT
    """
    def handle_CONNECT(self, connection):

        logger("Starting connection attempt for: {}".format(connection))
        self.sendACKW(connection)

        self.server.socketModule.reply(RDY, connection)

        Identifier = self.server.socketModule.read(connection).decode("UTF-8").replace("\n", "")
        self.sendACKW(connection)

        if self.handle_login(Identifier) is False:
            self.server.socketModule.reply(RECJ, connection)
            return

        self.authorized_users[connection] = Identifier
        self.server.socketModule.reply(ACCP, connection)

        logger("Connection opened")
    

    """
    APP         <-->        SERVER
    CLOSE                   ACKW
                            TERM
    ACKW
    """
    def handle_CLOSE(self, connection):

        logger("Attempting to close connection for {}".format(connection))

        self.sendACKW(connection)

        self.server.socketModule.reply(TERM, connection)
        
        data =  self.server.socketModule.read(connection)

        if self.protocolCompare(data.decode("utf-8").replace("\n", ""), ACKW.decode()):
            logger("Connection closed!")
            connection.close()
        else:
            logger("Failed to close connection")
            pass
        


    """
    APP         <-->        SERVER
    FILESEND
                            ACKW
    FILNAVN
                            ACKW
    FILESIZE
                            ACKW
    FILDATA
                            ACKW
    FILEFIN                         
                            ACKW                     

    """
    def handle_FILESEND(self, connection):
        
        USERNAME = self.authorized_users[connection]
        if USERNAME == "":
            return

        logger("Recieving FILE from {} for user: {}".format(connection, USERNAME))
        self.sendACKW(connection)   

        FILENAME =  self.server.socketModule.read(connection).decode("utf-8")
        self.sendACKW(connection)

        #Redo FILE transfer if done in chunks
        FILESIZE =  int(self.server.socketModule.read(connection).decode("utf-8"))
        self.sendACKW(connection)

        FILEDATA = bytearray()
        BYTES_RECIEVED = 0

  #      DATA = ""

        while True:
                    
            BYTES_TO_RECIEVE = connection.recv(128) 

            if(not BYTES_TO_RECIEVE):
                break

            if len(BYTES_TO_RECIEVE) + BYTES_RECIEVED > FILESIZE:
                BYTES_TO_RECIEVE = BYTES_TO_RECIEVE[:FILESIZE-BYTES_RECIEVED] # trim additional data
            
            FILEDATA += BYTES_TO_RECIEVE
            BYTES_RECIEVED += len(BYTES_TO_RECIEVE)

            if BYTES_RECIEVED == FILESIZE:
                break

                
        data =  self.server.socketModule.read(connection)

        if(data):
            data = data.decode("utf-8")
        else:
            return

        if self.protocolCompare(data.replace("\n", ""), FILE_FIN.decode()):

            if ( self.server.fHandler.createUserFile(USERNAME, FILENAME, FILEDATA) ) :
                self.sendACKW(connection)
            else:
                self.sendERRO(connection)
            
            


    """
    APP         <-->            SERVER
    FILESYNC
                                ACKW
                                NUMBER_OF_FILES
    ACKW
                                FILNAVN
    ACKW
                                FILESIZE
    ACKW
                                FILDATA

                                FILNAVN
    
                                

                                ...

                                FILFIN
                                ...
    """


    def handleFileTransfer(self, connection, file):

        f = open(file, "rb")
        BYTES_SENT = 0

        if(f):

            # Send filename
            self.server.socketModule.reply(file, connection)
            self.checkACKW(connection)

            # Send file size

            f.seek(0, os.SEEK_END)
            BYTES_TO_SEND = f.tell()
            f.seek(0, 0)

            self.server.socketModule.reply(str(BYTES_TO_SEND), connection)
            self.checkACKW(connection)

            # Send file data
            while(True):
                DATA = f.read(MAX_TRANSFER)
                BYTES_SENT += len(DATA)
                connection.send(DATA)

                if BYTES_SENT == BYTES_TO_SEND:
                    break
        logger("Sent file: {} size: {}".format(file, BYTES_SENT))




    def handle_FILESYNC(self, connection):

        self.sendACKW(connection)

        USERNAME = self.authorized_users[connection]

        if(USERNAME):

            logger("Syncing FILE for user: {}".format(USERNAME))

            FILES = self.server.fHandler.getUserFiles(USERNAME)

            if(len(FILES) > 0):

                self.server.socketModule.reply(str(len(FILES)), connection)
                self.checkACKW(connection)

                for i in range(0, len(FILES)):

                    self.handleFileTransfer(connection, FILES[i])

                self.server.socketModule.reply(FILE_FIN, connection)
            else:
                self.server.socketModule.reply(0, connection)

