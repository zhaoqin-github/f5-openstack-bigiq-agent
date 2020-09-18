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

    def icontrol_rest(self):
        pass

    def as3_deploy(self):
        pass

    def deploy_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        pass

    def create_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        partition = ("tenant-" + loadbalancer['tenant_id'] +
                     "-loadbalancer-" + loadbalancer['id'])
        uri = ("/mgmt/shared/resolver/device-groups"
               "/cm-bigip-allBigIpDevices/devices/" + bigip_id +
               "/rest-proxy/mgmt/tm/sys/folder")
        body = {
            "name": partition,
            "subPath": "/",
            "fullPath": "/" + partition
        }

        try:
            self.client.make_request(uri, method="POST", body=body)
        except Exception as ex:
            if isinstance(ex, HTTPError) and \
               ex.message.find("code: 409") >= 0:
                pass
            else:
                LOG.error("Fail to create loadbalancer %s : %s",
                          loadbalancer['id'], ex.message)
                raise ex

    def update_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        pass

    def delete_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        partition = ("tenant-" + loadbalancer['tenant_id'] +
                     "-loadbalancer-" + loadbalancer['id'])
        uri = ("/mgmt/shared/resolver/device-groups"
               "/cm-bigip-allBigIpDevices/devices/" + bigip_id +
               "/rest-proxy/mgmt/tm/sys/folder/~" + partition)

        try:
            self.client.make_request(uri, method="DELETE")
        except Exception as ex:
            if isinstance(ex, HTTPError) and \
               ex.message.find("code: 404") >= 0:
                pass
            else:
                LOG.error("Fail to delete loadbalancer %s : %s",
                          loadbalancer['id'], ex.message)
                raise ex

    def create_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        partition = ("tenant-" + loadbalancer['tenant_id'] +
                     "-loadbalancer-" + loadbalancer['id'])
        destination = (loadbalancer['vip_address'] + ":" +
                       str(listener['protocol_port']))
        uri = ("/mgmt/shared/resolver/device-groups"
               "/cm-bigip-allBigIpDevices/devices/" + bigip_id +
               "/rest-proxy/mgmt/tm/ltm/virtual")
        body = {
            "name": "listener-" + listener['id'],
            "partition": partition,
            "destination": destination,
            "ipProtocol": "tcp"
        }

        try:
            self.client.make_request(uri, method="POST", body=body)
        except Exception as ex:
            LOG.error("Fail to create listener %s : %s",
                      listener['id'], ex.message)
            raise ex

    def delete_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        partition = ("tenant-" + loadbalancer['tenant_id'] +
                     "-loadbalancer-" + loadbalancer['id'])
        uri = ("/mgmt/shared/resolver/device-groups"
               "/cm-bigip-allBigIpDevices/devices/" + bigip_id +
               "/rest-proxy/mgmt/tm/ltm/virtual/~" + partition +
               "~listener-" + listener['id'])

        try:
            self.client.make_request(uri, method="DELETE")
        except Exception as ex:
            if isinstance(ex, HTTPError) and \
               ex.message.find("code: 404") >= 0:
                pass
            else:
                LOG.error("Fail to delete listener %s : %s",
                          listener['id'], ex.message)
                raise ex
