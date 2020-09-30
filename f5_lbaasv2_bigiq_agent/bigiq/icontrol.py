from oslo_log import log as logging

from f5sdk.exceptions import HTTPError

from .manager import BIGIQManager

LOG = logging.getLogger(__name__)

bigip_root = ("/mgmt/shared/resolver/device-groups"
              "/cm-bigip-allBigIpDevices/devices/")

sys_root = "/rest-proxy/mgmt/tm/sys"

ltm_root = "/rest-proxy/mgmt/tm/ltm"

monitor_path = {
    "PING": "icmp",
    "TCP": "tcp",
    "HTTP": "http",
    "HTTPS": "https"
}


class BIGIQManagerIControl(BIGIQManager):
    """BIG-IQ Manager which utilizes iControl REST"""

    def __init__(self, conf):
        super(BIGIQManagerIControl, self).__init__(conf)

    def _create(self, uri, body, **kwargs):
        resource = kwargs.get("resource", "unknown")
        try:
            self.client.make_request(uri, method="POST", body=body)
        except Exception as ex:
            if isinstance(ex, HTTPError) and \
               ex.message.find("code: 409") >= 0:
                self._overwrite(uri, body, **kwargs)
            else:
                LOG.error("Fail to create %s : %s", resource, ex.message)
                raise ex

    def _overwrite(self, uri, body, **kwargs):
        resource = kwargs.get("resource", "unknown")
        try:
            self.client.make_request(uri, method="PUT", body=body)
        except Exception as ex:
            LOG.error("Fail to overwrite %s : %s", resource, ex.message)
            raise ex

    def _modify(self, uri, body, **kwargs):
        resource = kwargs.get("resource", "unknown")
        try:
            self.client.make_request(uri, method="PATCH", body=body)
        except Exception as ex:
            LOG.error("Fail to modify %s : %s", resource, ex.message)
            raise ex

    def _delete(self, uri, **kwargs):
        resource = kwargs.get("resource", "unknown")
        try:
            self.client.make_request(uri, method="DELETE")
        except Exception as ex:
            if isinstance(ex, HTTPError) and \
               ex.message.find("code: 404") >= 0:
                pass
            else:
                LOG.error("Fail to delete %s : %s", resource, ex.message)
                raise ex

    def create_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        uri = "{0}{1}{2}/folder".format(bigip_root, bigip_id, sys_root)
        body = {
            "name": partition,
            "description": "tenant-" + loadbalancer['tenant_id'],
            "subPath": "/",
            "fullPath": "/" + partition
        }
        self._create(uri, body, resource=partition)

    def delete_loadbalancer(self, bigip_id, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        uri = "{0}{1}{2}/folder/~{3}".format(
            bigip_root, bigip_id, sys_root, partition)
        self._delete(uri, resource=partition)

    def create_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        listener_name = "listener-" + listener['id']
        destination = (loadbalancer['vip_address'] + ":" +
                       str(listener['protocol_port']))
        uri = "{0}{1}{2}/virtual".format(bigip_root, bigip_id, ltm_root)
        body = {
            "name": listener_name,
            "partition": partition,
            "destination": destination,
            "ipProtocol": "tcp"
        }
        self._create(uri, body, resource=listener_name)

    def delete_listener(self, bigip_id, listener, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        listener_name = "listener-" + listener['id']
        uri = "{0}{1}{2}/virtual/~{3}~{4}".format(
            bigip_root, bigip_id, ltm_root, partition, listener_name)
        self._delete(uri, resource=listener_name)

    def create_pool(self, bigip_id, pool, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        pool_name = "pool-" + pool['id']
        uri = "{0}{1}{2}/pool".format(bigip_root, bigip_id, ltm_root)
        body = {
            "name": pool_name,
            "partition": partition
        }
        self._create(uri, body, resource=pool_name)

    def delete_pool(self, bigip_id, pool, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        pool_name = "pool-" + pool['id']
        uri = "{0}{1}{2}/pool/~{3}~{4}".format(
            bigip_root, bigip_id, ltm_root, partition, pool_name)
        self._delete(uri, resource=pool_name)

    def create_member(self, bigip_id, member, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        pool_name = "pool-" + member['pool_id']
        member_name = "member-" + member['id'] + ":" + \
                      str(member['protocol_port'])
        uri = "{0}{1}{2}/pool/~{3}~{4}/members".format(
            bigip_root, bigip_id, ltm_root, partition, pool_name)
        body = {
            "name": member_name,
            "address": member['address'],
            "partition": partition
        }
        self._create(uri, body, resource=member_name)

    def delete_member(self, bigip_id, member, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        pool_name = "pool-" + member['pool_id']
        member_name = "member-" + member['id'] + ":" + \
                      str(member['protocol_port'])
        uri = "{0}{1}{2}/pool/~{3}~{4}/members/~{3}~{5}".format(
            bigip_root, bigip_id, ltm_root, partition, pool_name, member_name)
        self._delete(uri, name="member", resource=member_name)

    def create_monitor(self, bigip_id, monitor, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        monitor_name = "monitor-" + monitor['id']
        uri = "{0}{1}{2}/monitor/{3}".format(
            bigip_root, bigip_id, ltm_root,
            monitor_path[monitor['type']])
        body = {
            "name": monitor_name,
            "partition": partition
        }
        self._create(uri, body, resource=monitor_name)

    def delete_monitor(self, bigip_id, monitor, loadbalancer, **kwargs):
        partition = "loadbalancer-" + loadbalancer['id']
        monitor_name = "monitor-" + monitor['id']
        uri = "{0}{1}{2}/monitor/{5}/~{3}~{4}".format(
            bigip_root, bigip_id, ltm_root, partition, monitor_name,
            monitor_path[monitor['type']])
        self._delete(uri, resource=monitor_name)
