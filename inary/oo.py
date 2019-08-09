# -*- coding: utf-8 -*-
#

# Guido's cool metaclass examples. fair use. ahahah.
# I find these quite handy. Use them :)

class autoprop(type):
    def __init__(cls, name, bases, dict):
        super(autoprop, cls).__init__(name, bases, dict)
        props = {}
        for name in list(dict.keys()):
            if name.startswith("_get_") or name.startswith("_set_"):
                props[name[5:]] = 1
        for name in list(props.keys()):
            fget = getattr(cls, "_get_{}".format(name), None)
            fset = getattr(cls, "_set_{}".format(name), None)
            setattr(cls, name, property(fget, fset))


class autosuper(type):
    def __init__(cls, name, bases, dict):
        super(autosuper, cls).__init__(name, bases, dict)
        setattr(cls, "_{}__super".format(name), super(cls))


class autosuprop(autosuper, autoprop):
    pass


class autoeq(type):
    """useful for structures"""

    def __init__(cls, name, bases, dict):
        super(autoeq, cls).__init__(name, bases, dict)

        def equal(self, other):
            return self.__dict__ == other.__dict__

        cls.__eq__ = equal


class Struct(metaclass=autoeq):
    def __init__(self, **entries):
        self.__dict__.update(entries)
