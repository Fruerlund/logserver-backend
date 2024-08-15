from debugger import logger
import os

"""
[MAIN FOLDER]

    [LOGS]

        [USER]
            [FILE1]
            [FILE1]
            [FILE1]
        [USER]
            [FILE1]
            [FILE1]
            [FILE1]
        [USER]
            [FILE1]
            [FILE1]
            [FILE1]
"""


LOG_DIRECTORY = os.getcwd()

class fHandler(object):

    # Setup
    """
    """
    def __init__(self, server):
        
        logger("Created: {} CWD: {}".format(self, os.getcwd()))
        self.server = server

        self.logDir = "logs"
        self.cwd = LOG_DIRECTORY+"/"+self.logDir
        self.basedir = self.cwd

        try:
            os.chdir(self.cwd)
        except:
            self.createLogDirectory()


    # Directory handling
    """
    """
    def createLogDirectory(self):
        try:
            os.mkdir(self.cwd)
            logger("Directory created at: {}".format(self.cwd))
        except FileExistsError:
            logger("File directory already exists at: \n{}".format(self.cwd))



    """
    """
    def createUserDirectory(self, username):

        try:
            os.mkdir( self.basedir + "/" + username)
        except FileExistsError:
            logger("User directory already exists!")


    """
    """
    def setUserDirectory(self, username):
        try:
            os.chdir(self.basedir+"/"+username)
            self.cwd = os.getcwd()
        except:
            self.createUserDirectory(username)
            self.cwd = self.basedir + "/" + username


    # File handling
    """
    """
    def createUserFile(self, username, filename, data):
        

        try: 
            self.setUserDirectory(username)

            logger("Creating file: {}".format(filename))
            os.chdir(self.cwd)
            with open(filename, "wb+") as f:
                #f.write(bytes(data.encode("UTF-8")))
                f.write(data)
                f.close()

            return True

        except Exception as e:
            logger(e)
            return False


    """
    """
    def deleteUserFile(self, username, filename):
        self.setUserDirectory(username)
        try:
            os.remove(self.cwd+"/"+filename)
        except FileNotFoundError:
            logger("File does not exists!")

    
    """
    """
    def getUserFiles(self, username):
        Files = list()
        try:
            os.chdir(self.cwd+"/"+username)
            for f in os.listdir(os.getcwd()):
                logger("FILE: {}".format(f))
                Files.append(f)
            return Files
        except Exception as e:
            logger(e)
            return []
        

    """
    """
    def getUserFileNumber(self, username):
        
        return len(self.getUserFiles(username))


    """
    """
    def handle_upload(self, filename, data):
        pass


    """
    """
    def handle_sync(self):
        pass
