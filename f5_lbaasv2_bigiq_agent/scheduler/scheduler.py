from oslo_log import log as logging

from .filter import filter_cls_map


LOG = logging.getLogger(__name__)


class BIGIPScheduler(object):
    """Base class of filters."""
    filter_instances = []

    def __init__(self, filter_names):
        for filter_name in filter_names:
            filter_class = filter_cls_map.get(filter_name)
            if filter_class is None:
                LOG.error("Filter class not found: %s", filter_name)
            else:
                self.filter_instances.append(filter_class())

    def schedule(self, bigips):
        candidates = bigips
        for ins in self.filter_instances:
            candidates = ins.filter_all(candidates)
        return candidates
