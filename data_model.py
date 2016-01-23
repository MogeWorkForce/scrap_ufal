import json

class TO(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if isinstance(value, (dict, )):
                self.__dict__[key] = TO(**value)
            else:
                self.__dict__[key] = value

    def __setattr__(self, attr, value):
        if isinstance(value, (dict, )):
            self.__dict__[attr] = TO(**value)
        else:
            self.__dict__[attr] = value

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __repr__(self):
        if not self.__dict__:
            return '{}'
        return self.to_json()

    def __iter__(self):
        return self.__dict__.iteritems()

    def __getitem__(self, attr):
        return self.__dict__[str(attr)]

    def __contains__(self, attr):
        return attr in self.__dict__

    def to_json(self):
        tmp = {}
        for key, item in self.__dict__.iteritems():
            tmp[key] = recursive_acces(key, item)
        return json.dumps(tmp)

    def pop(self, attr):
        return self.__dict__.pop(str(attr))

def recursive_acces(key, obj):
    tmp_data = {}
    if isinstance(obj, (dict,)):
        tmp_data[key] = {}
        for k, val in obj.iteritems():
            tmp_data[k] = recursive_acces(k, val)

    elif isinstance(obj, (TO, )):
        for k, val in obj:
            tmp_data[k] = recursive_acces(k, val)
    else:
        return obj

    return tmp_data

if __name__ == '__main__':
    d = TO(**{'0': ['maria']})
    print d
    d.name = {"familia": 'host', "casa": 15}
    t = TO()
    t.test = d
    print t
    print 'name' in t.test
    print t.test.pop(0)
    print t.test.name.casa


