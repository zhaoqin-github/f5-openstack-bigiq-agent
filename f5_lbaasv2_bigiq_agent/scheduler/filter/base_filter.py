import random


class BaseFilter(object):
    """Base class of filters."""
    def filter_one(self, bigip):
        return True

    def filter_all(self, bigips):
        return filter(self.filter_one, bigips)


class ActiveFilter(BaseFilter):
    """Active BIG-IP filter."""
    def filter_one(self, bigip):
        if bigip.get('state') and bigip['state'] == "ACTIVE":
            return True
        else:
            return False


class RandomFilter(BaseFilter):
    """Random BIG-IP filter."""
    def filter_all(self, bigips):
        return [bigips[random.randint(0, len(bigips) - 1)]]
