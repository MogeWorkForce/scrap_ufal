# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import requests
import re
import time

match = re.compile(r'<table class="tabela">(.*?)<\/table>')
get_paginator = re.compile(r'<span[^>]*class="paginaAoRedor">(.*?)</span>')
links = re.compile(r'<a[^>]*href="(?P<links>.*)?">.*?</a>')
match_th = re.compile(r'<th[^>]*?>(?P<content_th>[^<]*?)</th>')
match_td = re.compile(r'<(?:td|a)[^>]*?(?:href="(?P<link_document>[^"]*?)")?>(?P<content_td>[^<]*?)</(?:td|a)>')
match_tr_content = re.compile(
        r'<(?:td|span|tr)\s?(?:colspan="[^"]*?"|class="(?P<class>[^"]*?)")?>(?P<content_line>[^<]*?)<\/(?:td|span|tr)>'
    )

match_tr = re.compile(
        r'<tr.*?>(?P<content_tr>.*?)<\/tr>'
    )

def get_content_page(url, original_link=None):
    result = requests.get(url)
    no_spaces = clean_result(result)
    load_content(no_spaces)

def load_content(content):
    table_content = match.findall(content)
    for table in table_content:
        #for i, content in enumerate(match_tr.finditer(table)):
        #    print i, content.group('content_tr')
        for th in match_th.finditer(table):
            print th.group("content_th")

        for td in match_td.finditer(table):
            print td.group("content_td"), td.group('link_document')

def clean_result(result):
    return result.text.replace('\n', '').replace('  ', '')

url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115'
url_base = "http://www.portaltransparencia.gov.br"

result = requests.get(url)
no_spaces = clean_result(result)
print url
load_content(no_spaces)

paginator = get_paginator.findall(no_spaces)
print paginator
visited_link = []
for pg in paginator:
    for link_url in links.finditer(pg):
        link_ = link_url.group('links')
        print link_
        time.sleep(1)
        if link_ not in visited_link:
            get_content_page(url_base+link_)
            visited_link.append(link_)


