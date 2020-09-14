import importlib
import pkgutil

from inspect import isclass

filter_cls_map = {}

__path__ = pkgutil.extend_path(__path__, __name__)
for _, module_name, _ in pkgutil.walk_packages(path=__path__,
                                               prefix=__name__+'.'):
    module = importlib.import_module(module_name)
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if isclass(attribute) and attribute_name != "BaseFilter":
            filter_cls_map[attribute_name] = attribute
