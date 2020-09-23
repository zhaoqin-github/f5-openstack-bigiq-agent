from oslo_log import log as logging

from f5sdk.exceptions import HTTPError

from .manager import BIGIQManager

LOG = logging.getLogger(__name__)


class BIGIQManagerIControl(BIGIQManager):
    """BIG-IQ Manager which utilizes iControl REST"""

    def __init__(self, conf):
        super(BIGIQManagerIControl, self).__init__(conf)

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
