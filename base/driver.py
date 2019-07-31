from .feat import Feat

class Driver(object):

    @property
    def dev_name(self):
        raise NotImplementedError("A Driver should implement a device name")

    def __init__(self,name=None):
        if name: self._name = "{} ({})".format(name,self.dev_name)
        else: self._name = self.dev_name
        print("Connecting to: "+self._name)

    def get_config(self):
        feature_list = []
        for cls in self.__class__.mro():
            feature_list.extend([k for k,v in cls.__dict__.items() if type(v) in (Feat,property)])
        return { self._name : { feature: getattr(self,feature) for feature in feature_list } }

    def set_feat_log_mode(self,feature,get_log=None,set_log=None):
        feat = self.__class__.__dict__[feature]
        if get_log is not None : feat.is_get_logged = get_log
        if set_log is not None : feat.is_set_logged = set_log
