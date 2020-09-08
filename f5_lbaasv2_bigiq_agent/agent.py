import service_launcher
import sys

from oslo_config import cfg
from oslo_log import log as oslo_logging
from neutron.common import config as common_config
from neutron.common import rpc as n_rpc
from neutron.conf.agent import common as config

try:
    # q version
    from neutron.conf.agent.common import INTERFACE_OPTS
except Exception:
    # p version
    from neutron.agent.linux.interface import OPTS as INTERFACE_OPTS
except ImportError as Error:
    pass

import f5_lbaasv2_bigiq_agent.agent_manager as manager
import f5_lbaasv2_bigiq_agent.constants as constants

LOG = oslo_logging.getLogger(__name__)

OPTS = [
]


class F5BIGIQAgentService(n_rpc.Service):
    """F5 BIG-IQ agent service class."""

    def start(self):
        """Start the F5 agent service."""
        self.tg.add_timer(
            cfg.CONF.periodic_interval,
            self.manager.run_periodic_tasks,
            None,
            None
        )
        super(F5BIGIQAgentService, self).start()


def main():
    """F5 BIG-IQ agent for OpenStack."""
    cfg.CONF.register_opts(OPTS)
    cfg.CONF.register_opts(manager.OPTS)
    cfg.CONF.register_opts(INTERFACE_OPTS)

    config.register_agent_state_opts_helper(cfg.CONF)
    config.register_root_helper(cfg.CONF)

    common_config.init(sys.argv[1:])
    config.setup_logging()

    mgr = manager.F5BIGIQAgentManager(cfg.CONF)

    svc = F5BIGIQAgentService(
        host=mgr.agent_host,
        topic=constants.TOPIC_LBAASV2_BIGIQ_AGENT,
        manager=mgr
    )

    service_launch = service_launcher.F5ServiceLauncher(cfg.CONF)
    service_launch.launch_service(svc)
    service_launch.wait()
