# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import calendar
import copy
import logging
import os
import random
from datetime import date, timedelta, datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MODE = os.environ.get('MODE', 'DEV')

logger = logging.getLogger('Scrap_Ufal.DocumentsDao')
logger.setLevel(logging.DEBUG)

uri_url = 'MONGO_URI: ' + os.environ.get('MONGODB_ADDON_DB', '')
mongo_db = 'MONGO_DB: ' + os.environ.get('MONGODB_ADDON_URI', '')
logger.debug('\n\n')
logger.debug('-' * 30)
logger.debug(uri_url)
logger.debug(mongo_db)

logger.debug('\n\n')
logger.debug('-' * 30)


class DocumentsDao(MongoClient):
    PATTERN_PK = '%Y%m%d'
    NOT_ALLOWED_CLEAN = ('documentos_relacionados',)

    def __init__(self, *args, **kwargs):
        super(DocumentsDao, self).__init__(*args, **kwargs)
        if MODE == "PROD":
            self.db_empenho = self[os.environ['MONGODB_ADDON_DB']]
        else:
            self.db_empenho = self.notas_empenho
        self.documents = self.db_empenho.documents
        self.url = UrlManagerDao(*args, **kwargs)

    def insert_document(self, doc, upsert=False):
        try:
            date_ = date.today()
            key = {"_id": doc['dados_basicos']['documento'][0]}
            doc = self.adapt_docs_relacionados(doc)
            doc['date_saved'] = int(date_.strftime(self.PATTERN_PK))
            self.documents.replace_one(key, doc, upsert=upsert)
            logger.debug(('save:', key))
            url_ = doc['geral_data']['url_base'] + '/'
            url_ += doc['geral_data']['session'] + "/"
            url_ += doc['geral_data']['type_doc']
            url_ += '?documento=' + doc['geral_data']['num_doc']
            self.url.dynamic_url('queue', url_)

        except DuplicateKeyError as e:
            logger.error(e)
            logger.debug("move on - DuplicateKey")

    def adapt_docs_relacionados(self, doc):
        tmp_docs = doc["documentos_relacionados"]
        doc["documentos_relacionados"] = [
            {
                "data": tmp_docs["data"][i],
                "unidade_gestora": tmp_docs["unidade_gestora"][i],
                "orgao_superior": tmp_docs["orgao_superior"][i],
                "orgao_entidade_vinculada":
                    tmp_docs["orgao_entidade_vinculada"][i],
                "favorecido": tmp_docs["favorecido"][i],
                "fase": tmp_docs["fase"][i],
                "especie": tmp_docs["especie"][i],
                "elemento_de_despesa": tmp_docs["elemento_de_despesa"][i],
                "documento": tmp_docs["documento"][i],
                "valor_rs": float(tmp_docs["valor_rs"][i]) if
                tmp_docs["valor_rs"][i] else 0.00,
            } for i in xrange(len(tmp_docs["fase"]))
            ]
        doc = self.remove_list(doc)
        return doc

    def remove_list(self, doc):
        tmp_doc = {}
        for key, value in doc.iteritems():
            if key in self.NOT_ALLOWED_CLEAN:
                tmp_doc[key] = value
                continue
            new_value = None
            if isinstance(value, (dict,)):
                new_value = self.remove_list(value)
            elif isinstance(value, (list, tuple, set)):
                new_value = value[0] if len(value) == 1 else value
            tmp_doc[key] = new_value if new_value else value

        return tmp_doc


class UrlManagerDao(MongoClient):
    PATTERN_PK = '%Y%m%d'
    PATTERN_PK_MONTH = '%Y%m'
    LIMIT_DATE_REQUEST = datetime(2010, 5, 25)

    def __init__(self, *args, **kwargs):
        super(UrlManagerDao, self).__init__(*args, **kwargs)
        if MODE == "PROD":
            self.db_urls = self[os.environ['MONGODB_ADDON_DB']]
        else:
            self.db_urls = self.urls
        self.queue = self.db_urls.queue
        self.fallback = self.db_urls.fallback
        self.finder_urls_notas = self.db_urls.finder_urls_notas

    def set_chunk_url(self, list_url):
        date_ = date.today()
        key = {"_id": int(date_.strftime(self.PATTERN_PK))}
        data = {
            "$addToSet": {
                "urls": {"$each": list_url}
            }
        }

        skip = False
        try:
            tmp = copy.deepcopy(key)
            tmp.update({"urls": list_url})
            self.db_urls.queue.insert_one(tmp)
            skip = True
        except DuplicateKeyError as e:
            logger.debug(
                "Expected error - move on addToSet - Queue - DuplicateKey")

        if not skip:
            try:
                self.queue.update_one(key, data)
            except DuplicateKeyError as e:
                logger.error(e)
                logger.debug("move on - DuplicateKey - Queue")

    def dynamic_url(self, collection, url):
        date_ = date.today()
        key = {"_id": int(date_.strftime(self.PATTERN_PK))}
        data = {
            "$addToSet": {
                "urls": url
            }
        }
        skip = False
        try:
            tmp = copy.deepcopy(key)
            tmp.update({"urls": [url]})
            self.db_urls[collection].insert_one(tmp)
            skip = True
        except DuplicateKeyError as e:
            logger.debug(
                "Expected error - move on - %s - DuplicateKey",
                collection.capitalize())

        if not skip:
            try:
                self.db_urls[collection].update_one(key, data)
            except DuplicateKeyError as e:
                logger.error(e)
                logger.debug(
                    "move on -  %s - DuplicateKey", collection.capitalize())

    def remove_urls(self, list_urls, collection='queue'):
        date_ = date.today()
        key = {"_id": int(date_.strftime(self.PATTERN_PK))}
        data = {
            "$pullAll": {
                "urls": list_urls
            }
        }

        self.db_urls[collection].update(key, data)

    def verify_today_urls(self, url, collection='queue_loaded'):
        date_ = date.today()
        params = {
            "_id": int(date_.strftime(self.PATTERN_PK)),
            "urls": {"$in": [url]}
        }

        result = self.db_urls[collection].find(params)
        return bool(list(result))

    def add_period_to_recover_in_portal(self, date_start, month_elapse,
                                        params_search=None):
        # TODO: Change this name in future
        key = {"_id": int(date_start.strftime(self.PATTERN_PK_MONTH))}

        if date_start < self.LIMIT_DATE_REQUEST:
            date_start = self.LIMIT_DATE_REQUEST

        last_day_of_first_month = calendar.monthrange(
            date_start.year, date_start.month)[1]

        end_month = datetime(
            date_start.year, date_start.month, last_day_of_first_month)

        data = {
            'date_start': date_start,
            'date_end': end_month
        }
        data.update(key)
        self.insert_url_finder(data, params_search)

        if month_elapse > 1:
            new_start_date = end_month + timedelta(days=1)
            self.add_period_to_recover_in_portal(new_start_date,
                                                 month_elapse - 1)

    def insert_url_finder(self, data, params=None):
        try:
            if params and isinstance(params, (dict,)):
                params = {}
            data.update({'params': params})
            self.finder_urls_notas.insert(data)
        except DuplicateKeyError as e:
            logger.error(e)
            logger.debug("DuplicateKey on - %s", 'Finder Urls Notas')

    def random_finder_urls_notas(self, many_items):
        instances = self.finder_urls_notas.find()
        size_instances = instances.count()
        if size_instances > many_items:
            random_start = random.randint(0, size_instances)
            end_batch = random_start + many_items
            return list(instances)[random_start:end_batch]
        return instances


class ProxiesDao(MongoClient):
    def __init__(self, *args, **kwargs):
        super(ProxiesDao, self).__init__(*args, **kwargs)
        if MODE == "PROD":
            self.db_proxy = self[os.environ['MONGODB_ADDON_DB']]
        else:
            self.db_proxy = self.proxy
        self.proxies = self.db_proxy.proxies
        self.error_proxies = self.db_proxy.error_proxies

    def insert_proxies(self, list_proxy):
        if not isinstance(list_proxy, (list, tuple)):
            list_proxy = [list_proxy]

        list_proxy = [
            {
                'in_use': False,
                'proxy': x['proxy'],
                'localization': x['localization']
            } for x in list_proxy
            ]
        self.proxies.insert_many(list_proxy)

    def get_unused_proxy(self):
        random_skip = random.randint(0, 200)
        now = datetime.now() - timedelta(minutes=10, seconds=30)
        list_proxy = self.proxies.find({
            'in_use': False,
            "last_date_in_use": {
                "$lte": int(now.strftime("%Y%m%d%H%M%S"))
            }
        }).skip(random_skip).limit(1)
        if not list_proxy:
            raise Exception('No one proxy is free in this moment')

        proxy = list_proxy[0]
        logger.debug("Random Proxy choised are: %s", proxy)

        self.proxies.update_one(
            {"_id": proxy['_id']}, {"$set": {"in_use": True}})
        return proxy

    def mark_unused_proxy(self, key, error=False):
        now = datetime.now()
        self.proxies.update_one({"_id": key},
                                {"$set": {
                                    "in_use": False,
                                    "last_date_in_use": int(
                                        now.strftime("%Y%m%d%H%M%S"))
                                }})
        logger.debug('release key(%s)', key)
        if error:
            proxy_error = self.proxies.find_one({"_id": key})
            self.error_proxies.insert_one({'payload': proxy_error})

    def release_all_proxies(self):
        now = datetime.now()
        self.proxies.update_many({"in_use": True},
                                 {"$set": {
                                     "in_use": False,
                                     "last_date_in_use": int(
                                         now.strftime("%Y%m%d%H%M%S"))
                                 }})
        logger.debug('Release key all proxies')


class SystemConfigDao(MongoClient):
    def __init__(self, *args, **kwargs):
        super(SystemConfigDao, self).__init__(*args, **kwargs)
        if MODE == "PROD":
            self.db_system = self[os.environ['MONGODB_ADDON_DB']]
        else:
            self.db_system = self.conf_system
        self.configs = self.db_system.configs

    def get_configs(self):
        conf = self.configs.find_one({})
        if not conf:
            raise Exception('Configs are not setted')
        return conf
