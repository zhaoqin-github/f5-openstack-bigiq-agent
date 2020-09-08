from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging
import oslo_messaging
from oslo_service import loopingcall
from oslo_service import periodic_task

from neutron.agent import rpc as agent_rpc
from neutron_lib import context as ncontext

from f5_lbaasv2_bigiq_agent import constants
from f5_lbaasv2_bigiq_agent import plugin_rpc

LOG = logging.getLogger(__name__)

PERIODIC_TASK_INTERVAL = 60

OPTS = [
    cfg.IntOpt(
        'periodic_interval',
        default=PERIODIC_TASK_INTERVAL,
        help='Seconds between periodic task runs'
    ),
    cfg.BoolOpt(
        'start_agent_admin_state_up',
        default=True,
        help='Should the agent force its admin_state_up to True on boot'
    ),
    cfg.StrOpt(
        'provider_name',
        default='f5networks',
        help=('provider_name for snat pool addresses')
    ),
    cfg.StrOpt(
        'agent_id',
        default='12345678',
        help=('Static agent ID to use with Neutron')
    ),
    cfg.StrOpt(
        'bigiq_host',
        default='10.145.73.220',
        help=('BIG-IQ hostname or IP address')
    )
]


class F5BIGIQAgentManager(periodic_task.PeriodicTasks):
    """Periodic task that is an endpoint for plugin to agent RPC."""

    RPC_API_VERSION = '1.0'

    target = oslo_messaging.Target(version='1.0')

    def __init__(self, conf):
        """Initialize BIG-IQ Agent Manager."""
        super(F5BIGIQAgentManager, self).__init__(conf)
        LOG.debug("Initializing BIG-IQ Agent Manager")

        self.conf = conf
        self.context = ncontext.get_admin_context_without_session()
        self.serializer = None

        self.agent_host = self.conf.agent_id

        global PERIODIC_TASK_INTERVAL
        PERIODIC_TASK_INTERVAL = self.conf.periodic_interval

        # Initialize agent configurations
        agent_configurations = ({
            'bigiq_host': self.conf.bigiq_host
        })

        # Initialize agent-state to a default values
        self.admin_state_up = self.conf.start_agent_admin_state_up

        self.agent_state = {
            'binary': constants.AGENT_BINARY_NAME,
            'host': self.conf.agent_id,
            'topic': constants.TOPIC_LBAASV2_BIGIQ_AGENT,
            'agent_type': constants.LBAASV2_BIGIQ_AGENT_TYPE,
            'configurations': agent_configurations,
            'start_flag': True
        }

        # Setup RPC for communications to and from controller
        self._setup_rpc()

        # Mark this agent admin_state_up per startup policy
        if(self.admin_state_up):
            self.plugin_rpc.set_agent_admin_state(self.admin_state_up)

        # Start state reporting of agent to Neutron
        report_interval = self.conf.AGENT.report_interval
        if report_interval:
            heartbeat = loopingcall.FixedIntervalLoopingCall(
                self._report_state)
            heartbeat.start(interval=report_interval)

    def _setup_rpc(self):

        # Setting up outbound (callbacks) communications from agent

        # setup the topic to send oslo messages RPC calls
        # from this agent to the controller
        topic = constants.TOPIC_LBAASV2_BIGIQ_DRIVER

        # create our class we will use to send callbacks to the controller
        # for processing by the driver plugin
        self.plugin_rpc = plugin_rpc.LBaaSv2PluginRPC(
            self.context,
            topic,
            self.conf.agent_id
        )

        # Setting up outbound communcations with the neutron agent extension
        self.state_rpc = agent_rpc.PluginReportStateAPI(topic)

    def _report_state(self, force_resync=False):
        try:
            self.plugin_rpc.set_agent_admin_state(True)
            LOG.debug("reporting state of agent as: %s" % self.agent_state)
            self.state_rpc.report_state(self.context, self.agent_state)
            self.agent_state.pop('start_flag', None)
        except Exception as e:
            LOG.exception(("Failed to report state: " + str(e.message)))

    # callback from oslo messaging letting us know we are properly
    # connected to the message bus so we can register for inbound
    # messages to this agent
    def initialize_service_hook(self, started_by):
        """Create service hook to listen for messanges on agent topic."""
        node_topic = "%s.%s" % (constants.TOPIC_LBAASV2_BIGIQ_AGENT,
                                self.conf.agent_id)
        LOG.debug("Creating topic for consuming messages: %s" % node_topic)
        endpoints = [started_by.manager]
        started_by.conn.create_consumer(
            node_topic, endpoints, fanout=False)

    @periodic_task.periodic_task(
        spacing=PERIODIC_TASK_INTERVAL)
    def update_operating_status(self, context):
        pass

    ######################################################################
    #
    # handlers for all in bound requests and notifications from controller
    #
    ######################################################################
    @log_helpers.log_method_call
    def agent_updated(self, context, payload):
        """Handle the agent_updated notification event."""
        pass

    @log_helpers.log_method_call
    def create_loadbalancer(self, context, loadbalancer, **kwargs):
        """Handle RPC cast from plugin to create_loadbalancer."""
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_loadbalancer(self, context, old_loadbalancer,
                            loadbalancer, **kwargs):
        """Handle RPC cast from plugin to update_loadbalancer."""
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_loadbalancer(self, context, loadbalancer, **kwargs):
        """Handle RPC cast from plugin to delete_loadbalancer."""
        self.plugin_rpc.loadbalancer_destroyed(loadbalancer['id'])

    @log_helpers.log_method_call
    def update_loadbalancer_stats(self, context, loadbalancer, **kwarg):
        """Handle RPC cast from plugin to get stats."""
        pass

    @log_helpers.log_method_call
    def create_listener(self, context, listener, **kwarg):
        """Handle RPC cast from plugin to create_listener."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_listener(self, context, old_listener, listener, **kwarg):
        """Handle RPC cast from plugin to update_listener."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_listener(self, context, listener, **kwarg):
        """Handle RPC cast from plugin to delete_listener."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.listener_destroyed(listener['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def create_pool(self, context, pool, **kwarg):
        """Handle RPC cast from plugin to create_pool."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_pool(self, context, old_pool, pool, **kwarg):
        """Handle RPC cast from plugin to update_pool."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_pool(self, context, pool, **kwarg):
        """Handle RPC cast from plugin to delete_pool."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.pool_destroyed(pool['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def create_member(self, context, member, **kwarg):
        """Handle RPC cast from plugin to create_member."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_member(self, context, old_member, member, **kwarg):
        """Handle RPC cast from plugin to update_member."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_member(self, context, member, **kwarg):
        """Handle RPC cast from plugin to delete_member."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.member_destroyed(member['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def create_health_monitor(self, context, health_monitor, **kwarg):
        """Handle RPC cast from plugin to create_pool_health_monitor."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_health_monitor(self, context, old_health_monitor,
                              health_monitor, **kwarg):
        """Handle RPC cast from plugin to update_health_monitor."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_health_monitor(self, context, health_monitor, **kwarg):
        """Handle RPC cast from plugin to delete_health_monitor."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.health_monitor_destroyed(health_monitor['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def create_l7policy(self, context, l7policy, **kwarg):
        """Handle RPC cast from plugin to create_l7policy."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_l7policy(self, context, old_l7policy, l7policy, **kwarg):
        """Handle RPC cast from plugin to update_l7policy."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_l7policy(self, context, l7policy, **kwarg):
        """Handle RPC cast from plugin to delete_l7policy."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.l7policy_destroyed(l7policy['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def create_l7rule(self, context, l7rule, **kwarg):
        """Handle RPC cast from plugin to create_l7rule."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def update_l7rule(self, context, old_l7rule, l7rule, **kwarg):
        """Handle RPC cast from plugin to update_l7rule."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)

    @log_helpers.log_method_call
    def delete_l7rule(self, context, l7rule, **kwarg):
        """Handle RPC cast from plugin to delete_l7rule."""
        loadbalancer = kwarg['loadbalancer']
        self.plugin_rpc.l7rule_destroyed(l7rule['id'])
        self.plugin_rpc.update_loadbalancer_status(
            loadbalancer['id'], constants.ACTIVE, constants.ONLINE)
