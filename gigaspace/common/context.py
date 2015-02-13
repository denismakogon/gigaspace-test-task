__author__ = 'dmakogon'


class RequestContext(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            _key = key.replace("-", "_")
            setattr(self, _key, value)
