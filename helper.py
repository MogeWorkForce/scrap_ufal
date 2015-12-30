# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class Reader(object):
    def __init__(self, arq, *args, **kwargs):
        self.name_arq = arq
        self.__content = ''
    
    @property
    def text(self):
        if self.__content:
            return self.__content
        else:
            self.temp = open(self.name_arq, 'rb')
            self.__content = self.temp.read().decode('utf-8')
            return self.__content

    @property
    def content(self):
        return self.text
