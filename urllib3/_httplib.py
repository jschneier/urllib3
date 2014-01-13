'''
See also shazow/urllib3/#236
'''

from .collections_ import HTTPHeaderDict

import types

from httplib import (
    HTTPException, # for the public api
    HTTPMessage as _HTTPMessage,
    HTTPResponse as _HTTPResponse,
    HTTPConnection as _HTTPConnection
)

def clone(original, **newg):
    return types.FunctionType(original.func_code,
                              dict(original.func_globals, **newg),
                              original.func_name,
                              original.func_defaults,
                              original.func_closure)

def inject(cls, **newg):
    newdict = dict(cls.__dict__)

    for attr, func in cls.__dict__.items():
	if isinstance(func, types.FunctionType):
	    for k in newg:
	        if k in func.func_code.co_names:
		    newdict[attr] = clone(func, **newg)
		    break
    return types.ClassType(cls.__name__, (cls, ), newdict)

class HTTPMessage(_HTTPMessage):

    def __init__(self, fp, seekable=1):
        _HTTPMessage.__init__(self, fp, seekable)
        self._dict = HTTPHeaderDict()

        def _get_dict(self):
            return self._dict
        def _set_dict(self, value):
	    self._dict = HTTPHeaderDict(value)
        dict = property(_get_dict, _set_dict)

HTTPResponse = inject(_HTTPResponse, HTTPMessage=HTTPMessage)

class HTTPConnection(_HTTPConnection):
    response_class = HTTPResponse

try:
    import ssl
except ImportError:
    pass
else:
    from httplib import HTTPSConnection as _HTTPSConnection
    HTTPSConnection = inject(_HTTPSConnection, HTTPConnection=HTTPConnection)
