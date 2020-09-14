from oslo_log import log as logging

from f5sdk.bigiq import ManagementClient

LOG = logging.getLogger(__name__)


class BIGIQClient(object):
    """BIGIQ client"""

    def __init__(self, conf):
        self.conf = conf
        self.client = ManagementClient(
            conf.bigiq_host, user=conf.bigiq_user,
            password=conf.bigiq_password)

    def get_info(self):
        return self.client.get_info()
