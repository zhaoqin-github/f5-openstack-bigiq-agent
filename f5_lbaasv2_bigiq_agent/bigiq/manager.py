from oslo_log import log as logging

from f5sdk.bigiq import ManagementClient
from f5sdk.exceptions import HTTPError

LOG = logging.getLogger(__name__)


class BIGIQManager(object):
    """Base BIG-IQ Manager"""

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
            resp = self.client.make_request(uri, method="GET")
            return resp
        except HTTPError as ex:
            LOG.error(HTTPError.message)
            return None
        except Exception as ex:
            raise ex

    def get_devices_in_tenant_device_group(self, tenant_id):
        uri = ("/mgmt/shared/resolver/device-groups/tenant_" + tenant_id +
               "/devices?$filter=('product'+eq+'BIG-IP')")
        try:
            resp = self.client.make_request(uri, method="GET")
            return resp['items']
        except HTTPError as ex:
            LOG.error(HTTPError.message)
            return []
        except Exception as ex:
            raise ex

    def create_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        pass

    def update_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        pass

    def delete_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        pass

    def create_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        pass

    def update_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        pass

    def delete_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        pass

    def create_pool(self, bigip_id, pool, loadbalancer, **kwargs):
        pass

    def update_pool(self, bigip_id, pool, loadbalancer, **kwargs):
        pass

    def delete_pool(self, bigip_id, pool, loadbalancer, **kwargs):
        pass

    def create_member(self, bigip_id, member, loadbalancer, **kwargs):
        pass

    def update_member(self, bigip_id, member, loadbalancer, **kwargs):
        pass

    def delete_member(self, bigip_id, member, loadbalancer, **kwargs):
        pass

    def create_monitor(self, bigip_id, monitor, loadbalancer, **kwargs):
        pass

    def update_monitor(self, bigip_id, monitor, loadbalancer, **kwargs):
        pass

    def delete_monitor(self, bigip_id, monitor, loadbalancer, **kwargs):
        pass

    def create_l7policy(self, bigip_id, l7policy, loadbalancer, **kwargs):
        pass

    def update_l7policy(self, bigip_id, l7policy, loadbalancer, **kwargs):
        pass

    def delete_l7policy(self, bigip_id, l7policy, loadbalancer, **kwargs):
        pass

    def create_l7rule(self, bigip_id, l7rule, loadbalancer, **kwargs):
        pass

    def update_l7rule(self, bigip_id, l7rule, loadbalancer, **kwargs):
        pass

    def delete_l7rule(self, bigip_id, l7rule, loadbalancer, **kwargs):
        pass
