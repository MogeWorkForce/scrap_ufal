# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class Reader(object):
    def __init__(self, arq, *args, **kwargs):
        self.name_arq = arq
        self._content = []
    
    @property
    def text(self):
        if self._content:
            return self._content
        else:
            self.temp = open(self.name_arq, 'rb')
            self._content = self.temp.read().decode('utf-8')
            return self._content
