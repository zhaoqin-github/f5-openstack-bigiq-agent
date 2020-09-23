from .as3 import BIGIQManagerAS3
from .icontrol import BIGIQManagerIControl


def get_bigiq_mgr(conf):
    if conf.deploy_mode == "as3":
        return BIGIQManagerAS3(conf)
    else:
        return BIGIQManagerIControl(conf)
