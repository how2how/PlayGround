import logging
from controller.utils import XStream

logger = logging.getLogger(__name__)

logger.setLevel(10)

fh = logging.FileHandler('system.log')
logger.addHandler(fh)

# sh = logging.StreamHandler()
# logger.addHandler(sh)


formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
# sh.setFormatter(formatter)


class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write('%s\n' % record)
        # originally: XStream.stdout().write("{}\n".format(record))


qh = QtHandler()
logger.addHandler(qh)
qh.setFormatter(formatter)
