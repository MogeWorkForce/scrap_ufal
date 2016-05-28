# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import date
import logging
import traceback
import copy
import os

MODE = os.environ.get('MODE', 'DEV')

logger = logging.getLogger('Scrap_Ufal.DocumentsDao')
logger.setLevel(logging.DEBUG)

__author__ = 'hermogenes'

class DocumentsDao(MongoClient):

    def __init__(self, *args, **kwargs):
        super(DocumentsDao, self).__init__(*args, **kwargs)
        self.db_empenho = self.notas_empenho if MODE not in ['DEV', "DOCKER"] else self[
                                                                            os.environ.get('MONGODB_ADDON_DB', 'notas_empenho')
                                                                            ]
        self.documents = self.db_empenho.documents
        self._url = UrlManagerDao(*args, **kwargs)

    def insert_document(self, doc, upsert=False):
        try:
            key = {"_id": doc['dados_basicos']['documento'][0]}
            doc = self.adapt_docs_relacionados(doc)
            result = self.documents.replace_one(key, doc, upsert=upsert)
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
        self.db_urls = self.urls if MODE not in ['DEV', "DOCKER"] else self[
                                                                        os.environ.get('MONGODB_ADDON_DB', 'urls')
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
            result = self.db_urls.queue.insert_one(tmp)
            skip = True
        except DuplicateKeyError as e:
            logger.debug("Expected error - move on addToSet - DuplicateKey")

        if not skip:
            try:
                result = self.queue.update_one(key, data)
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
            result = self.db_urls[collection].insert_one(tmp)
            skip = True
        except DuplicateKeyError as e:
            logger.debug("Expected error - move on - DuplicateKey")

        if not skip:
            try:
                result = self.db_urls[collection].update_one(key, data)
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

        result = self.db_urls[collection].update(key, data)

    def verify_today_urls(self, url, collection='queue_loaded'):
        date_ = date.today()
        params = {
            "_id": int(date_.strftime(self.PATTERN_PK)),
            "urls": {"$in": [url]}
        }

        result = self.db_urls[collection].find(params)
        return bool(list(result))


def avaiable_aggregation(d, type_fase):
    import time
    start = time.time()
    i = 0
    for result in d.documents.find():
        result["documentos_relacionados"] = [
            {
                "data": tmp_docs["data"],
                "unidade_gestora": tmp_docs["unidade_gestora"],
                "orgao_superior": tmp_docs["orgao_superior"],
                "orgao_entidade_vinculada": tmp_docs["orgao_entidade_vinculada"],
                "favorecido": tmp_docs["favorecido"],
                "fase": tmp_docs["fase"],
                "especie": tmp_docs["especie"],
                "elemento_de_despesa": tmp_docs["elemento_de_despesa"],
                "documento": tmp_docs["documento"],
                "valor_rs": float(tmp_docs["valor_rs"]) if tmp_docs["valor_rs"] else 0.00,
            } for tmp_docs in result["documentos_relacionados"] if tmp_docs['fase'] == type_fase
        ]
        i+=1
    end = time.time()
    print "consumed", i, 'documents'
    #print "Took: ", end - start, "ms"
    #print "Start: ", start, "\n  End: ",end
    #return result

'''
var timerIt = function(){
    var start = (new Date()).getTime();
    var result = db.documents.aggregate(
        {"$match": {"_id": "2015NE800115"}},
        {"$unwind": "$documentos_relacionados"},
        {"$match": {"documentos_relacionados.fase": "Liquidação"}},
        {"$group": {"_id": "$_id", "documentos_relacionados": {"$push": "$documentos_relacionados"}}}
    );
    var end = (new Date()).getTime();
    print("Took: "+ (end - start));
    print("Start: "+start+"\nEnd: "+end); return result; };

'''