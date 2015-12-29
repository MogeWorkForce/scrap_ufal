# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from unicodedata import normalize
import requests
import re
import time
import logging
import helper
import json
import sys

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
                       r'/(?P<type_doc>[^?]*)?.*?=(?P<num_doc>[a-zA-Z0-9]*)'
                       r'&?(?:pagina=(?P<num_page>\d{1,3})#.*)?')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
match_subtable = re.compile(r'<table class="subtabela">(.*?)<\/table>')
get_paginator = re.compile(r'<span class="paginaXdeN">.*(?P<inicio>\d{1,3}?)'
                           r'.*(?P<fim>\d{1,3})</span>')
links = re.compile(r'<a[^>]*href="(?P<links>.*)?">.*?</a>')

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

def _normalize_text(txt, codif='utf-8'):
    if isinstance(txt, str):
        txt = txt.decode(codif, "ignore")
    return normalize('NFKD', txt).encode('ASCII', 'ignore').replace(" ", "_").replace(':', '').lower()

def get_content_page(url, original_link=None, data=None):
    if not data:
        data = {}
    num_page = base_data.findall(url)[0][-1]
    num_page = int(num_page) if num_page else 1
    paginator = False
    if num_page >1:
        paginator = True
        
    try:
        result = requests.get(url, timeout=10)
        print result.status
    except:
        page = 'page%s.html' % base_data.findall(url)[0][-1]
        print page
        result = helper.Reader(page)
        time.sleep(3)
        
    no_spaces = clean_result(result)
    data = load_content(no_spaces, paginator, data)
    return data

def load_content(content, paginator=False, data=None):
    table_content = match.findall(content)
    adjust_headers = []
    subtable = match_subtable.findall(content)
    content_subtable = []
    for i, subtable in enumerate(subtable):
        content_ = {}
        subtable_headers = []
        for j, content in enumerate(match_tr.finditer(subtable)):
            line_ = content.group('content_tr').strip()
            class_tr_sub = content.group('class_tr')
            for z, item in enumerate(match_content.finditer(line_)):
                content_value = item.group('content').strip()
                if class_tr_sub in ('cabecalho', ):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    subtable_headers.append(content_value)
                    content_[subtable_headers[-1]] = {}
                    continue
                else:
                    if not content_[subtable_headers[z]]:
                        content_[subtable_headers[z]] = [content_value]
                    else:
                        content_[subtable_headers[z]].append(content_value)
        content_subtable.append({"content": content_, "values": j})
    
    counter_subtable = 0
    if paginator:
        print 'paginator'
        table_content = table_content[-1:]

    for i, table in enumerate(table_content):
        head = []
        skip = False
        qt_lines_sub = -1
        if counter_subtable < len(content_subtable):
            qt_lines_sub = content_subtable[counter_subtable]['values']
        rotulo = []
        count_rotulo = 0
        duo_rotulo = False
        referency = 0
        class_tr_rotulo = ''
        for j, content in enumerate(match_tr.finditer(table)):
            line = content.group('content_tr').strip()
            
            if 'subtabela' in line:
                #print 'subtabela'
                data[head[0]][last_key_th] = content_subtable[counter_subtable]['content']
                counter_subtable += 1
                skip = True
                continue
            #print qt_lines_sub
            if skip and qt_lines_sub >= 0:
                qt_lines_sub -= 1
                continue
            else:
                skip = False

            class_tr = content.group('class_tr')
            last_key_tr = ''
            last_key_th = ''
            sub_head = []
            counter_sub_head = 1
            title = True
            #print head, sub_head, last_key_th, last_key_tr, rotulo
            for z, content_row in enumerate(match_content.finditer(line)):
                content_value = content_row.group('content').strip()
                #print z, content_value, line, head, sub_head, rotulo
                insert_value = True
                if class_tr in ('cabecalho', 'titulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_tr = content_value
                    head.append(last_key_tr)
                    if paginator:
                        continue
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
                if duo_rotulo and class_tr_rotulo != class_tr:
                        count_rotulo = 0
                        duo_rotulo = False

                if class_content and class_content in ('rotulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_th = content_value
                    sub_head.append(last_key_th)
                    rotulo.append(last_key_th)
                    count_rotulo +=1
                    #print 'j: %s, z: %s, c_rotulo: %s, class_tr: %s' % (j, z, count_rotulo, class_tr)
                    #print rotulo
                    if not duo_rotulo and count_rotulo == 2:
                        referency = j -1
                        duo_rotulo = True
                        class_tr_rotulo = class_tr
                    
                    if len(head) > 1:
                        if duo_rotulo:
                            data[head[0]][head[-1]][rotulo[referency]][sub_head[-1]] = {}
                        else:
                            data[head[0]][head[-1]][sub_head[-1]] = {}
                    else:
                        #print '-----', sub_head[-1],
                        #print '-----', data[head[0]]
                        if duo_rotulo:
                            #print 'j: ', rotulo, referency
                            data[head[0]][rotulo[referency]][sub_head[-1]] = {}
                        else:
                            data[head[0]][sub_head[-1]] = {}
                else:                       
                    count_rotulo -=1
                    #print 'j: %s, z: %s, c_rotulo: %s, class_tr: %s' % (j, z, count_rotulo, class_tr)
                    #print 'referency: %s, duo_rotulo: %s' % (referency, duo_rotulo)
                    
                    #print z, class_tr, head, sub_head, class_content, title
                    if len(head) > 1 and not sub_head:
                        if not data[head[0]][head[z+1]]:
                            data[head[0]][head[z+1]] = [content_value]
                        else:
                            data[head[0]][head[z+1]].append(content_value)
                    else:
                        #print head, sub_head, content_value, data

                        if not duo_rotulo:
                            if not data[head[0]][sub_head[-1]]:
                                data[head[0]][sub_head[-1]] = [content_value]
                            else:
                                data[head[0]][sub_head[-1]].append(content_value)
                        else:
                            if not data[head[0]][rotulo[referency]][sub_head[-1]]:
                                data[head[0]][rotulo[referency]][sub_head[-1]] = [content_value]
                            else:
                                data[head[0]][rotulo[referency]][sub_head[-1]].append(content_value)

                #link_document = content_row.group('link_document')
                #values_debug = [content_value, class_content, link_document]
                #values_debug = [temp for temp in values_debug if temp]
                #logger.debug(values_debug)
                #logger.debug("tr "+last_key_tr)
                #logger.debug("th "+last_key_th)
            #print i, j, head, sub_head, rotulo
    #logger.warning(json.dumps(data, indent=2))
    return data

def clean_result(result):
    return result.text.replace('\n', '').replace('  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')

url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/liquidacao?documento=153037152222015NS006140'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=364150362012015NE001171'
#url = 'http://portaltransparencia.gov.br/despesasdiarias/liquidacao?documento=153037152222015NS003530'
#url = 'http://portaltransparencia.gov.br/despesasdiarias/liquidacao?documento=513001579042015NS002737'
data_doc = {'geral_data': {}}
for dt in base_data.finditer(url):
    data_doc['geral_data']['url_base'] = dt.group("host")
    data_doc['geral_data']['type_doc'] = dt.group("type_doc")
    data_doc['geral_data']['num_doc'] = dt.group("num_doc")
    data_doc['geral_data']['session'] = dt.group("session")
    logger.debug(data_doc)

try:
    result = requests.get(url, timeout=10)
    data_doc['geral_data']['estatico'] = False
    data_doc['geral_data']['url'] = url
except:
    print 'leu um arquivo estatico'
    page = 'page1.html'
    print 'error'
    #page = 'liquidacao.html'
    #time.sleep(3)
    print page
    result = helper.Reader(page)
    #result = helper.Reader()
    data_doc['geral_data']['estatico'] = True
    data_doc['geral_data']['arquivo'] = page
no_spaces = clean_result(result)
load_content(no_spaces, data=data_doc)
print data_doc['geral_data'].get('url', 'estatico :(')
paginator = get_paginator.findall(no_spaces)
print paginator
#paginator = []
visited_link = []
end_link_paginator = '&pagina=%s#paginacao'
for pg in paginator:
    end, init = pg
    for next_pg in xrange(int(init)+1, int(end)+1):
        link_ = url+end_link_paginator % next_pg
        logger.debug(link_)
        if link_ not in visited_link:
            data_doc = get_content_page(link_, data=data_doc)
            visited_link.append(link_)

print data_doc
