import sys

DEBUG = WARNING = INFO = ERROR = CRITICAL = None

class Logger:
    def __init__(self, name):
        self.name = name
    
    def log(self, level=DEBUG, msg="", *args):
        print("%s: %s" % (self.name, msg % args), file=sys.stderr)
    
    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)
    
    exception = critical = error = warning = info = debug

log = Logger("uosc.fakelogger")

def basicConfig(*args, **kwargs):
    pass
    
def getLogger(name):
    return log
    
