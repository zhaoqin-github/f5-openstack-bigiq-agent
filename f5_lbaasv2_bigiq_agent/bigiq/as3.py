from oslo_log import log as logging

from .manager import BIGIQManager

LOG = logging.getLogger(__name__)


class BIGIQManagerAS3(BIGIQManager):
    """BIG-IQ Manager which utilizes AS3"""

    def __init__(self, conf):
        super(BIGIQManagerAS3, self).__init__(conf)
