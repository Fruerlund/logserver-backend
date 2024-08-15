import inspect

LOG = True
def logger(message):
    if(LOG):
        print("D/: {}() {}".format(inspect.stack()[1][3], message))