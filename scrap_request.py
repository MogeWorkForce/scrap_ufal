# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from unicodedata import normalize
from data_model.dao.mongodb import DocumentsDao
import requests
import re
import time
import logging
import json
import sys
import traceback
import argparse
from datetime import date

logger = logging.getLogger("Scrap_Ufal.scraper")
level_debug = logging.DEBUG
logger.setLevel(level_debug)

base_data = re.compile(r'(?P<host>http?://.*?)/(?P<session>[^/]*)'
                       r'/(?P<type_doc>[^?]*)?.*?=(?P<num_doc>[a-zA-Z0-9]*)'
                       r'&?(?:pagina=(?P<num_page>\d{1,3})#.*)?')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
match_subtable = re.compile(r'<table class="subtabela">(.*?)<\/table>')
get_paginator = re.compile(r'<span class="paginaXdeN">Página (?P<inicio>\d{1,3}?) de (?P<fim>\d{1,3})</span>')
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

client = DocumentsDao()

start_ = time.time()


def save_or_update(doc):
    client.insert_document(doc, upsert=True)


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
    
    data['geral_data']['url'] = url
    return data


#TODO: pessimo nome, mudar isso depois
def cleaned_content(url, visited_links):
    time.sleep(3.8)
    logger.debug((len(visited_links), url))
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    result = requests.get(url, timeout=10, headers=headers)
    visited_links.append(url)

    no_spaces = clean_result(result)
    return no_spaces
    

def get_content_page(url, visited_links=None, data=None):
    if not data:
        data = {}

    if not visited_links:
        visited_links = []
    data = get_general_data(url, data)
    paginator = False

    result = cleaned_content(url, visited_links)

    no_spaces = result
    data = load_content(no_spaces, paginator, data, visited_links)
    return data


def load_content(content_original, paginator=False, data=None, visited_links=None):
    if not visited_links:
        visited_links = []
        
    table_content = match.findall(content_original)
    subtable = match_subtable.findall(content_original)
    content_subtable = []

    docs_relacionados = []
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
            for z, content_row in enumerate(match_content.finditer(line)):
                content_value = content_row.group('content').strip()
                if class_tr in ('cabecalho', 'titulo'):
                    content_value = _normalize_text(content_value).replace('_/_', '_')
                    last_key_tr = content_value
                    head.append(last_key_tr)
                    if paginator:
                        continue
                    if class_tr == 'titulo':
                        data[head[-1]] = {}
                        continue
                    else:
                        data[head[0]][head[-1]] = {}
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
                    new_url = data['geral_data']['url_base']+'/'+data['geral_data']['session']+'/'+link_document
                    if new_url not in visited_links:
                        docs_relacionados.append(new_url)
    
    if not paginator:
        paginas = get_paginator.findall(content_original)
        end_link_paginator = '&pagina=%s#paginacao'
        for pg in paginas[:1]:
            _, end = pg
            for next_pg in xrange(1, int(end)+1):
                url_ = data['geral_data']['url_base']+'/'+data['geral_data']['session']+"/"
                url_ += data['geral_data']['type_doc']+'?documento='+data['geral_data']['num_doc']
                if next_pg == 1:
                    link_ = url_
                else:
                    link_ = url_+end_link_paginator % next_pg

                if link_ not in visited_links:
                    result = cleaned_content(link_, visited_links)
                    no_spaces = result
                    data = load_content(no_spaces, True, data, visited_links)

    if not paginator:
        save_or_update(data)
        
    client._url.set_chunk_url(docs_relacionados)

    return data


def clean_result(result):
    return result.text.replace('\n', '').replace('  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')


def load_url_from_queue(batch=1, collection='queue'):
    try:
        import random
        logger.debug('----- start new job! (%s) Batches: %s' % (collection.upper(), batch))
        date_ = date.today()
        key = {"_id": date_.strftime("%d/%m/%Y")}
        urls_load = client._url.db_urls[collection].find_one(key)

        length_urls = len(urls_load['urls'])

        if length_urls <= 0:
            logger.warning("(%s) Finish the Process all Urls" % collection.upper())
            return
        elif length_urls == 1:
            init_ = 0
        else:
            init_ = random.randint(0, length_urls+1)
        
        logger.debug("(%s) Interval %s to %s" % (collection.upper(), init_, init_+batch))
        tmp_urls_load = urls_load['urls'][init_:init_+batch]

        visited_link = []
        for url in tmp_urls_load:
            try:
                in_ = client._url.verify_today_urls(url)

                if not in_:
                    logger.debug('Start load url_from %s! %s' % (collection.upper(), url))
                    get_content_page(url, visited_links=visited_link)
                    client._url.dinamic_url('queue_loaded', url)
                else:
                    logger.warning("Url already loaded: %s" % url)
            except:
                traceback.print_exc()
                client._url.dinamic_url('fallback', url)
                logger.warning("Call Fallback to Url: %s" % url)

        try:
            client._url.remove_urls(tmp_urls_load, collection=collection)
            logger.debug('(%s)Pass to remove_urls! Batches: %d' %(collection.upper(), batch))
        except Exception as e:
            traceback.print_exc()
            logger.warning("Error on remove urls")
            
    except:
        traceback.print_exc()
        logger.debug('Errors on %s!' % collection.upper())
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set a Url to crawler")
    parser.add_argument('-u', '--url', type=str,
                        help="Url to search notas_empenhos")

    parser.add_argument('-b', '--batch', type=int, choices=range(1, 21),
                        help="How many urls will be loaded inside the queue")


    args = parser.parse_args()
    if not args.url:
        raise Exception("Url not passed, please set a url in arguments")
    
    url = args.url

    data_doc = {}
    visited_link = [url]

    load_url_from_queue(batch=15)

    # data_doc = get_content_page(url, visited_links=visited_link)
    #
    # print 'content_doc principal: ', len(data_doc['documentos_relacionados']['fase'])
    # print 'links visitados: ', len(visited_link)

    #save_or_update(data_doc)

    print 'finish in: ', time.time() - start_

