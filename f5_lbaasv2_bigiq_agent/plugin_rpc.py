from oslo_log import helpers as log_helpers
from oslo_log import log as logging
import oslo_messaging as messaging

from neutron.common import rpc

from f5_openstack_agent.lbaasv2.drivers.bigip import constants_v2 as constants

LOG = logging.getLogger(__name__)


class LBaaSv2PluginRPC(object):
    """Client interface for agent to plugin RPC."""

    RPC_API_NAMESPACE = None

    def __init__(self, context, topic, host):
        """Initialize LBaaSv2PluginRPC."""
        super(LBaaSv2PluginRPC, self).__init__()

        if topic:
            self.topic = topic
        else:
            self.topic = constants.TOPIC_LBAASV2_BIGIQ_DRIVER

        self.target = messaging.Target(topic=self.topic,
                                       version=constants.RPC_API_VERSION)
        self._client = rpc.get_client(self.target, version_cap=None)

        self.context = context
        self.host = host

    def _make_msg(self, method, **kwargs):
        return {'method': method,
                'namespace': self.RPC_API_NAMESPACE,
                'args': kwargs}

    def _call(self, context, msg, **kwargs):
        return self.__call_rpc_method(context,
                                      msg,
                                      rpc_method='call',
                                      **kwargs)

    def _cast(self, context, msg, **kwargs):
        self.__call_rpc_method(context,
                               msg,
                               rpc_method='cast',
                               **kwargs)

    def _fanout_cast(self, context, msg, **kwargs):
        kwargs['fanout'] = True
        self.__call_rpc_method(context, msg, rpc_method='cast', **kwargs)

    def __call_rpc_method(self, context, msg, **kwargs):
        options = dict(
            ((opt, kwargs[opt])
             for opt in ('fanout', 'timeout', 'topic', 'version')
             if kwargs.get(opt))
        )
        if msg['namespace']:
            options['namespace'] = msg['namespace']

        if options:
            callee = self._client.prepare(**options)
        else:
            callee = self._client

        func = getattr(callee, kwargs['rpc_method'])
        return func(context, msg['method'], **msg['args'])

    @log_helpers.log_method_call
    def set_agent_admin_state(self, admin_state_up):
        """Set the admin_state_up of for this agent"""
        succeeded = False
        try:
            succeeded = self._call(
                self.context,
                self._make_msg('set_agent_admin_state',
                               admin_state_up=admin_state_up,
                               host=self.host),
                topic=self.topic
            )
        except messaging.MessageDeliveryFailure:
            LOG.error("agent->plugin RPC exception caught: ",
                      "set_agent_admin_state")

        return succeeded

    @log_helpers.log_method_call
    def update_loadbalancer_status(self,
                                   loadbalancer_id,
                                   provisioning_status=None,
                                   operating_status=None):
        """Update the database with loadbalancer status."""
        return self._cast(
            self.context,
            self._make_msg('update_loadbalancer_status',
                           loadbalancer_id=loadbalancer_id,
                           status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_loadbalancer_stats(self, loadbalancer_id, stats):
        """Update the database with loadbalancer stats."""
        return self._cast(
            self.context,
            self._make_msg('update_loadbalancer_stats',
                           loadbalancer_id=loadbalancer_id,
                           stats=stats),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def loadbalancer_destroyed(self, loadbalancer_id):
        """Delete the loadbalancer from the database."""
        return self._cast(
            self.context,
            self._make_msg('loadbalancer_destroyed',
                           loadbalancer_id=loadbalancer_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_listener_status(self,
                               listener_id,
                               provisioning_status=constants.F5_ERROR,
                               operating_status=constants.F5_OFFLINE):
        """Update the database with listener status."""
        return self._cast(
            self.context,
            self._make_msg('update_listener_status',
                           listener_id=listener_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def listener_destroyed(self, listener_id):
        """Delete listener from database."""
        return self._cast(
            self.context,
            self._make_msg('listener_destroyed',
                           listener_id=listener_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_pool_status(self,
                           pool_id,
                           provisioning_status=constants.F5_ERROR,
                           operating_status=constants.F5_OFFLINE):
        """Update the database with pool status."""
        return self._cast(
            self.context,
            self._make_msg('update_pool_status',
                           pool_id=pool_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def pool_destroyed(self, pool_id):
        """Delete pool from database."""
        return self._cast(
            self.context,
            self._make_msg('pool_destroyed',
                           pool_id=pool_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_member_status(self,
                             member_id,
                             provisioning_status=None,
                             operating_status=None):
        """Update the database with member status."""
        return self._cast(
            self.context,
            self._make_msg('update_member_status',
                           member_id=member_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def member_destroyed(self, member_id):
        """Delete member from database."""
        return self._cast(
            self.context,
            self._make_msg('member_destroyed',
                           member_id=member_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_health_monitor_status(
            self,
            health_monitor_id,
            provisioning_status=constants.F5_ERROR,
            operating_status=constants.F5_OFFLINE):
        """Update the database with health_monitor status."""
        return self._cast(
            self.context,
            self._make_msg('update_health_monitor_status',
                           health_monitor_id=health_monitor_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def health_monitor_destroyed(self, health_monitor_id):
        """Delete health_monitor from database."""
        return self._cast(
            self.context,
            self._make_msg('health_monitor_destroyed',
                           health_monitor_id=health_monitor_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_l7rule_status(
            self,
            l7rule_id,
            l7policy_id,
            provisioning_status=constants.F5_ERROR,
            operating_status=constants.F5_OFFLINE):
        return self._cast(
            self.context,
            self._make_msg('update_l7rule_status',
                           l7rule_id=l7rule_id,
                           l7policy_id=l7policy_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def l7rule_destroyed(self, l7rule_id):
        """Delete health_monitor from database."""
        return self._cast(
            self.context,
            self._make_msg('l7rule_destroyed',
                           l7rule_id=l7rule_id),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def update_l7policy_status(
            self,
            l7policy_id,
            provisioning_status=constants.F5_ERROR,
            operating_status=constants.F5_OFFLINE):
        return self._cast(
            self.context,
            self._make_msg('update_l7policy_status',
                           l7policy_id=l7policy_id,
                           provisioning_status=provisioning_status,
                           operating_status=operating_status),
            topic=self.topic
        )

    @log_helpers.log_method_call
    def l7policy_destroyed(self, l7policy_id):
        return self._cast(
            self.context,
            self._make_msg('l7policy_destroyed',
                           l7policy_id=l7policy_id),
            topic=self.topic
        )
