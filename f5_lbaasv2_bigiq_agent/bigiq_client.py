from oslo_log import log as logging

from f5sdk.bigiq import ManagementClient
from f5sdk.exceptions import HTTPError

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

    def get_tenant_device_group(self, tenant_id):
        uri = "/mgmt/shared/resolver/device-groups/tenant_" + tenant_id
        try:
            resp = self.client.make_request(uri)
            return resp
        except HTTPError as ex:
            LOG.error(HTTPError.message)
            return None
        except Exception as ex:
            raise ex

    def get_devices_in_tenant_device_group(self, tenant_id):
        uri = "/mgmt/shared/resolver/device-groups/tenant_" + \
              tenant_id + "/devices?$filter=('product'+eq+'BIG-IP')"
        try:
            resp = self.client.make_request(uri)
            return resp['items']
        except HTTPError as ex:
            LOG.error(HTTPError.message)
            return []
        except Exception as ex:
            raise ex

    def icontrol_rest():
        pass

    def as3_deploy():
        pass
