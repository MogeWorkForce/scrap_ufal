# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from unicodedata import normalize
import requests
import re
import time
import logging
import helper
import json

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
match_subtable = re.compile(r'<table class="subtabela">(.*?)<\/table>')
get_paginator = re.compile(r'<span\s?(?:class="paginaAoRedor")?[^>]?>'
                           r'(.*?)</span>')
links = re.compile(r'<a[^>]*href="(?P<links>.*)?">.*?</a>')
##match_content = re.compile(
##    r'<(?:t(?:d|h)|a|span)[^>]*?(?:href="(?P<link_document>[^"]*?)"'
##    r'|class="(?P<class>[^"]*?)")?\s?(?:colspan=".*"?)?>(?P<content>[^<]*?)'
##    r'</(?:t(?:d|h)|a|span)>'
##)

##match_content = re.compile(
##    r'<(?:t(?:d|h)|a|span)[^>]*?(?:href="(?P<link_document>[^"]*?)")?'
##    r'\s?(?:class="(?P<class>[^"]*?)")?\s?(?:colspan=".*"?)?>(?P<content>[^<]*?)'
##    r'</(?:t(?:d|h)|a|span)>'
##)

match_content = re.compile(
    r'<(?:t(?:d|h)|a|span)[^>]*?(?:href="(?P<link_document>[^"]*?)")?'
    r'\s?(?:class="(?P<class>[^"]*?)")?.*?>(?P<content>[^<]*?)</(?:t(?:d|h)|a|span)>'
)

match_tr_content = re.compile(
    r'<(?:td|span|tr)\s?(?:colspan="[^"]*?"|class="(?P<class>[^"]*?)")?>'
    r'(?P<content_line>[^<]*?)<\/(?:td|span|tr)>'
)

match_tr = re.compile(
    r'<tr\s?(?:class="(?P<class_tr>[^"]*)")?.*?>(?P<content_tr>.*?)<\/tr>'
)

match_tr_subtable = re.compile(r'<tr\s?(?:class="(?P<class_subtable_tr>[^"]*?)").*?>(?P<content_subclass>.*)<\/tr>')
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
    adjust_headers = []
    subtable = match_subtable.findall(content)
    content_subtable = {}
    for i, subtable in enumerate(subtable):
        subtable_headers = []
        for j, content in enumerate(match_tr.finditer(subtable)):
            line_ = content.group('content_tr').strip()
            class_tr_sub = content.group('class_tr')
            for z, item in enumerate(match_content.finditer(line_)):
                content_value = item.group('content').strip()
                if class_tr_sub in ('cabecalho', ):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    subtable_headers.append(content_value)
                    content_subtable[subtable_headers[-1]] = {}
                    continue
                else:
                    if not content_subtable[subtable_headers[z]]:
                        content_subtable[subtable_headers[z]] = [content_value]
                    else:
                        content_subtable[subtable_headers[z]].append(content_value)
    qt_lines_sub = j
    for i, table in enumerate(table_content):
        head = []
        counter_subtable = 0
        skip = False
        for j, content in enumerate(match_tr.finditer(table)):
            line = content.group('content_tr').strip()
            
            if 'subtabela' in line:
                data[head[0]][last_key_th] = content_subtable
                counter_subtable += 1
                skip = True
                continue

            if skip and qt_lines_sub >= 0:
                qt_lines_sub -= 1
                continue
            else:
                skip = False

            class_tr = content.group('class_tr')
            last_key_tr = ''
            last_key_th = ''
            sub_head = []
            rotulo = []
            counter_sub_head = 1
            title = True
            print line, head, sub_head
            for z, content_row in enumerate(match_content.finditer(line)):
                content_value = content_row.group('content').strip()
                #print z, content_value, line
                insert_value = True
                if class_tr in ('cabecalho', 'titulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_tr = content_value
                    head.append(last_key_tr)
                    if class_tr == 'titulo':
                        title = True
                        data[head[-1]] = {}
                        continue
                    else:
                        #print head
                        data[head[0]][head[-1]] = {}
                        title = False
                        continue

                class_content = content_row.group('class')
                if class_content and class_content in ('rotulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_th = content_value
                    sub_head.append(last_key_th)
                    if len(head) > 1:
                        data[head[0]][head[-1]][sub_head[-1]] = {}
                    else:
                        data[head[0]][sub_head[-1]] = {}
                else:
                    #print z, class_tr, head, sub_head, class_content, title
                    if len(head) > 1:
                        if not sub_head:
                            if not data[head[0]][head[z+1]]:
                                data[head[0]][head[z+1]] = [content_value]
                            else:
                                data[head[0]][head[z+1]].append(content_value)
                    else:
                        if not sub_head and len(head)>1:
                            if not data[head[0]][head[z+1]]:
                                data[head[0]][head[z+1]] = [content_value]
                            else:
                                data[head[0]][head[z+1]].append(content_value)
                        else:
                            print head, sub_head, content_value
                            if not data[head[0]][sub_head[-1]]:
                                data[head[0]][sub_head[-1]] = [content_value]
                            else:
                                data[head[0]][sub_head[-1]].append(content_value)

##                if title:
##                    print 'outros trs sao conteudos'

                link_document = content_row.group('link_document')
                values_debug = [content_value, class_content, link_document]
                values_debug = [temp for temp in values_debug if temp]
                logger.debug(values_debug)
                logger.debug("tr "+last_key_tr)
                logger.debug("th "+last_key_th)
            #print i, j, head, sub_head
    logger.warning(json.dumps(data))

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

try:
    result = requests.get(url, timeout=10)
except:
    result = helper.Reader('page1.html')
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


