import json

class TO(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
        	self.__dict__[key] = value

    def __setattr__(self, attr, value):
    	self.__dict__[attr] = value

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __repr__(self):
    	if not self.__dict__:
    		return '{}'
    	tmp = {}
    	for key, item in self.__dict__.iteritems():
    		tmp[key] = recursive_acces(key, item)
    	return "{}".format(json.dumps(tmp))

    def __iter__(self):
    	return self.__dict__.iteritems()

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
	d = TO()
	print d
	d.name = 'host'
	t = TO()
	t.test = d
	print t
	print t.test
	
