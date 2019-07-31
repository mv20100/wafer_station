import logging
logger = logging.getLogger('driver')

class Feat(object):

    name = None
    is_get_logged = False
    is_set_logged = False

    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset

    def getter(self, func):
        if not self.name: self.name = func.__name__
        self.fget = func
        return self

    def setter(self, func):
        if not self.name: self.name = func.__name__
        self.fset = func
        return self
            
    def __get__(self, instance, owner=None):
        if self.fget is None:
            raise AttributeError("Can't get attribute {!s}".format(self.name))
        # print("In __get__ ", instance)
        value = self.fget(instance)
        if self.is_get_logged:
            logger.log(logging.INFO, "GET {}.{} = {}".format(instance._name,self.name,value))
        return value      

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("Can't set attribute {!s}".format(self.name))
        # print("In __set__ ", instance)
        self.fset(instance, value)
        if self.is_set_logged:
            logger.log(logging.INFO, "SET {}.{} TO {}".format(instance._name,self.name,value))
