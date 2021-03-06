from termcolor import colored
import logging


class ColorizeFilter(logging.Filter):

    color_by_level = {
        # logging.TRACE: 'white',
        logging.DEBUG: 'white',
        logging.INFO: 'yellow',
        logging.WARN: 'cyan',
        logging.ERROR: 'red',
    }

    def filter(self, record):
        record.raw_msg = record.msg
        color = self.color_by_level.get(record.levelno)
        if color:
            record.msg = colored(record.msg, color)
        return True

def showProgress(part, full):
    percent = float(part) / full

    sys.stdout.write("\r(%2d%%) Processed %5d/%5d links" % (
        round(percent * 100), part, full
    ))
    sys.stdout.flush()

def getDefaultUser():
    user = None
    try:
        import getpass
        user = getpass.getuser()
        del getpass
    except (ImportError, KeyError):
        # either no getpass module or no entry in OS db for user
        user = ''
    return user
