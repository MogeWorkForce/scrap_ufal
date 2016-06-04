# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import date
import logging
import copy
import os

MODE = os.environ.get('MODE', 'DEV')

logger = logging.getLogger('Scrap_Ufal.DocumentsDao')
logger.setLevel(logging.DEBUG)

uri_url = 'MONGO_URI: '+os.environ.get('MONGODB_ADDON_DB', '')
mongo_db = 'MONGO_DB: '+os.environ.get('MONGODB_ADDON_URI', '')
logger.debug('\n\n')
logger.debug('-' * 30)
logger.debug(uri_url)
logger.debug(mongo_db)

logger.debug('\n\n')
logger.debug('-' * 30)


class DocumentsDao(MongoClient):

    def __init__(self, *args, **kwargs):
        super(DocumentsDao, self).__init__(*args, **kwargs)
        self.db_empenho = self.notas_empenho if MODE in ['DEV', "DOCKER"] else self[
                                                                            os.environ.get('MONGODB_ADDON_DB')
                                                                            ]
        self.documents = self.db_empenho.documents
        self._url = UrlManagerDao(*args, **kwargs)

    def insert_document(self, doc, upsert=False):
        try:
            key = {"_id": doc['dados_basicos']['documento'][0]}
            doc = self.adapt_docs_relacionados(doc)
            self.documents.replace_one(key, doc, upsert=upsert)
            logger.debug(('save:', key))
            url_ = doc['geral_data']['url_base']+'/'+doc['geral_data']['session']+"/"
            url_ += doc['geral_data']['type_doc']+'?documento='+doc['geral_data']['num_doc']
            self._url.dinamic_url('queue', url_)

        except DuplicateKeyError as e:
            print e
            logger.debug("move on - DuplicateKey")

    def adapt_docs_relacionados(self, doc):
        tmp_docs = doc["documentos_relacionados"]
        doc["documentos_relacionados"] = [
            {
                "data": tmp_docs["data"][i],
                "unidade_gestora": tmp_docs["unidade_gestora"][i],
                "orgao_superior": tmp_docs["orgao_superior"][i],
                "orgao_entidade_vinculada": tmp_docs["orgao_entidade_vinculada"][i],
                "favorecido": tmp_docs["favorecido"][i],
                "fase": tmp_docs["fase"][i],
                "especie": tmp_docs["especie"][i],
                "elemento_de_despesa": tmp_docs["elemento_de_despesa"][i],
                "documento": tmp_docs["documento"][i],
                "valor_rs": float(tmp_docs["valor_rs"][i]) if tmp_docs["valor_rs"][i] else 0.00,
            } for i in xrange(len(tmp_docs["fase"]))
        ]
        return doc


class UrlManagerDao(MongoClient):
    PATTERN_PK = '%Y%m%d'
    def __init__(self, *args, **kwargs):
        super(UrlManagerDao, self).__init__(*args, **kwargs)
        self.db_urls = self.urls if MODE in ['DEV', "DOCKER"] else self[
                                                                        os.environ.get('MONGODB_ADDON_DB')
                                                                    ]
        self.queue = self.db_urls.queue
        self.fallback = self.db_urls.fallback

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
            logger.debug("Expected error - move on addToSet - DuplicateKey")

        if not skip:
            try:
                self.queue.update_one(key, data)
            except DuplicateKeyError as e:
                print e
                logger.debug("move on - DuplicateKey")

    def dinamic_url(self, collection, url):
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
            logger.debug("Expected error - move on - DuplicateKey")

        if not skip:
            try:
                self.db_urls[collection].update_one(key, data)
            except DuplicateKeyError as e:
                print e
                logger.debug("move on - DuplicateKey")

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
