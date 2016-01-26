# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from unicodedata import normalize
from data_model.to import TO
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import requests
import re
import time
import logging
import helper
import json
import sys
import traceback
import argparse

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
    r'<(?:t(?:d|h)|a|span)[^>]*?\s?(?:class="(?P<class>[^"]*?)")?.*?'
    r'(?:href="(?P<link_document>[^"]*?)")?>(?P<content>[^<]*?)</(?:t(?:d|h)|a|span)>'
)
match_tr_content = re.compile(
    r'<(?:td|span|tr)\s?(?:colspan="[^"]*?"|class="(?P<class>[^"]*?)")?>'
    r'(?P<content_line>[^<]*?)<\/(?:td|span|tr)>'
)

match_tr = re.compile(
    r'<tr\s?(?:class="(?P<class_tr>[^"]*)")?.*?>(?P<content_tr>.*?)<\/tr>'
)

match_tr_subtable = re.compile(r'<tr\s?(?:class="(?P<class_subtable_tr>[^"]*?)").*?>(?P<content_subclass>.*)<\/tr>')

client = MongoClient()
db = client.notas_empenho
collect = db.documents

start_ = time.time()

def save_or_update(doc):
    try:
        key = {"_id": doc['dados_basicos']['documento'][0]}
        result = collect.replace_one(key,doc,upsert=True)
    except DuplicateKeyError as e:
        print e
        logger.debug("move on - DuplaceteKey")
    except KeyError as e:
        traceback.print_exc()
        logger.debug("move on")

def try_numeric(value):
    try:
        tmp_value = value.replace("R$", "")
        value = float(tmp_value)
    except:
        pass
    return value

def _normalize_text(txt, codif='utf-8'):
    if isinstance(txt, str):
        txt = txt.decode(codif, "ignore")
    return normalize('NFKD', txt).encode('ASCII', 'ignore').\
        replace(" ", "_").\
        replace(':', '').\
        replace("(","").\
        replace(")","").\
        replace("$", "s").lower()

def get_general_data(url, data=None):
    if not data:
        data = {'geral_data': {}}
    if 'geral_data' not in data:
        data['geral_data'] = {}
        
    for dt in base_data.finditer(url):
        data['geral_data']['url_base'] = dt.group("host")
        data['geral_data']['type_doc'] = dt.group("type_doc")
        data['geral_data']['num_doc'] = dt.group("num_doc")
        data['geral_data']['session'] = dt.group("session")

    print base_data.findall(url)[0]
    
    data['geral_data']['url'] = url
    return data

    
def get_content_page(url, visited_links=None, data=None):
    if not data:
        data = {}

    if not visited_links:
        visited_links = []
    data = get_general_data(url, data)
    type_session = base_data.findall(url)[0][2]
    num_page = base_data.findall(url)[0][-1]
    num_page = int(num_page) if num_page else 1
    paginator = False
    if num_page >1:
        paginator = True
        
    try:
        logger.debug((len(visited_links), url))
        time.sleep(0.5)
        result = requests.get(url, timeout=10)
    except:
        #page = 'page%s.html' % base_data.findall(url)[0][-1]

        #if type_session == 'liquidacao':
        #    page = 'liquidacao.html'
        #print page
        #result = helper.Reader(page)
        return data
        
    no_spaces = clean_result(result)
    data = load_content(no_spaces, paginator, data, visited_links)
    return data

def load_content(content, paginator=False, data=None, visited_links=None):
    if not visited_links:
        visited_links = []
        
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
                    content_value = try_numeric(content_value)
                    if not content_[subtable_headers[z]]:
                        content_[subtable_headers[z]] = [content_value]
                    else:
                        content_[subtable_headers[z]].append(content_value)
        content_subtable.append({"content": content_, "values": j})
    
    counter_subtable = 0
    if paginator:
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
                data[head[0]][last_key_th] = content_subtable[counter_subtable]['content']
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
            counter_sub_head = 1
            title = True
            for z, content_row in enumerate(match_content.finditer(line)):
                content_value = content_row.group('content').strip()
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
                        if duo_rotulo:
                            data[head[0]][rotulo[referency]][sub_head[-1]] = {}
                        else:
                            data[head[0]][sub_head[-1]] = {}
                else:                       
                    count_rotulo -=1
                    content_value = try_numeric(content_value)
                    if len(head) > 1 and not sub_head:
                        if not data[head[0]][head[z+1]]:
                            data[head[0]][head[z+1]] = [content_value]
                        else:
                            data[head[0]][head[z+1]].append(content_value)
                    else:
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

                link_document = content_row.group('link_document')
                if link_document:
                    new_url = data_doc['geral_data']['url_base']+'/'+data_doc['geral_data']['session']+'/'+link_document
                    if new_url not in visited_links:
                        visited_links.append(new_url)
                        #TODO: Save content in another document
                        new_doc = get_content_page(url=new_url, visited_links=visited_links)
                        save_or_update(new_doc)
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

#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/liquidacao?documento=153037152222015NS008591'
#url = 'http://www.portaltransparencia.gov.br/despesasdiarias/empenho?documento=791800000012016NE000001'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set a Url to crawler")
    parser.add_argument('-u', '--url', type=str,
                        help="Url to search notas_empenhos")

    args = parser.parse_args()
    if not args.url:
        raise Exception("Url not passed, please set a url in arguments")
    
    url = args.url

    data_doc = {'geral_data': {}}
    data_doc = get_general_data(url, data_doc)
    print data_doc

    try:
        result = requests.get(url, timeout=10)
        data_doc['geral_data']['estatico'] = False
        data_doc['geral_data']['url'] = url
    except:
        raise Exception("Request fail")

    visited_link = [url]
    no_spaces = clean_result(result)
    load_content(no_spaces, data=data_doc, visited_links=visited_link)

    paginator = get_paginator.findall(no_spaces)
    end_link_paginator = '&pagina=%s#paginacao'
    for pg in paginator:
        end, init = pg
        for next_pg in xrange(int(init)+1, int(end)+1):
            link_ = url+end_link_paginator % next_pg
            logger.debug(link_)
            if link_ not in visited_link:
                data_doc = get_content_page(link_, data=data_doc, visited_links=visited_link)
                visited_link.append(link_)

    print 'content_doc principal: ', len(data_doc['documentos_relacionados']['fase'])
    print 'links visitados: ', len(visited_link)

    save_or_update(data_doc)

    print 'finish in: ', time.time() - start_

