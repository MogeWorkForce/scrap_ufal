# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import requests
import re
import time
import logging
from unicodedata import normalize

formatter = logging.Formatter(
    "[%(levelname)s][PID %(process)d][%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Scrap_Ufal")
level_debug = logging.DEBUG
logger.setLevel(level_debug)
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


base_data = re.compile(r'(?P<host>http?://.*?)/(?P<session>[^/]*)'
                       r'/(?P<type_doc>[^?]*)?.*?=(?P<num_doc>.*)')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
get_paginator = re.compile(r'<span\s?(?:class="paginaAoRedor")?[^>]?>'
                           r'(.*?)</span>')
links = re.compile(r'<a[^>]*href="(?P<links>.*)?">.*?</a>')
match_content = re.compile(
    r'<(?:t(?:d|h)|a|span)[^>]*?(?:href="(?P<link_document>[^"]*?)"'
    r'|class="(?P<class>[^"]*)"?)?>(?P<content>[^<]*?)'
    r'</(?:t(?:d|h)|a|span)>'
)
match_tr_content = re.compile(
    r'<(?:td|span|tr)\s?(?:colspan="[^"]*?"|class="(?P<class>[^"]*?)")?>'
    r'(?P<content_line>[^<]*?)<\/(?:td|span|tr)>'
)

match_tr = re.compile(
    r'<tr\s?(?:class="(?P<class_tr>[^"]*)")?.*?>(?P<content_tr>.*?)<\/tr>'
)
data = {'geral_data': {}}

def _normalize_text(txt, codif='utf-8'):
    if isinstance(txt, str):
        txt = txt.decode(codif, "ignore")
    return normalize('NFKD', txt).encode('ASCII', 'ignore').replace(" ", "_").replace(':', '').lower()

def get_content_page(url, original_link=None):
    result = requests.get(url, timeout=10)
    no_spaces = clean_result(result)
    load_content(no_spaces)

def load_content(content):
    table_content = match.findall(content)
    for j, table in enumerate(table_content):
        for i, content in enumerate(match_tr.finditer(table)):
            #logger.debug((i, content.group('content_tr'), content.group('class_tr')))
            line = content.group('content_tr').strip()
            class_tr = content.group('class_tr')
            last_key_tr = ''
            last_key_th = ''
            head = []
            sub_head = []
            counter_sub_head = 1
            title = False
            for content_row in match_content.finditer(line):
                content_value = content_row.group('content').strip()
                insert_value = True
                if class_tr in ('cabecalho', 'titulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_tr = content_value
                    head.append(last_key_tr)
                    if class_tr == 'titulo':
                        title = True
                    else:
                        title = False

                class_content = content_row.group('class')
                if class_content and class_content in ('rotulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_th = content_value
                    sub_head.append(last_key_th)

                link_document = content_row.group('link_document')
                values_debug = [content_value, class_content, link_document]
                values_debug = [temp for temp in values_debug if temp]
                logger.debug(values_debug)
                logger.debug("tr "+last_key_tr)
                logger.debug("th "+last_key_th)
            print j, i, head, sub_head

def clean_result(result):
    return result.text.replace('\n', '').replace('  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')

url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/liquidacao?documento=153037152222015NS006140'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=364150362012015NE001171'

for dt in base_data.finditer(url):
    data['geral_data']['url_base'] = dt.group("host")
    data['geral_data']['type_doc'] = dt.group("type_doc")
    data['geral_data']['num_doc'] = dt.group("num_doc")
    data['geral_data']['session'] = dt.group("session")
    logger.debug(data)

result = requests.get(url, timeout=10)
no_spaces = clean_result(result)
load_content(no_spaces)

paginator = get_paginator.findall(no_spaces)
print paginator
paginator = []
visited_link = []
for pg in paginator:
    for link_url in links.finditer(pg):
        link_ = link_url.group('links')
        logger.debug(data['geral_data']['url_base']+link_)
        if link_ not in visited_link:
            get_content_page(data['geral_data']['url_base']+link_)
            visited_link.append(link_)


