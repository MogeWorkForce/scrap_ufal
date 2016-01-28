# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging
import traceback
from datetime import date

logger = logging.getLogger('Scrap_Ufal.DocumentsDao')
logger.setLevel(logging.DEBUG)

__author__ = 'hermogenes'

class DocumentsDao(MongoClient):

    def __init__(self, *args, **kwargs):
        super(DocumentsDao, self).__init__(*args, **kwargs)
        self.db_empenho = self.notas_empenho
        self.documents = self.db_empenho.documents
        self._url = UrlManagerDao()

    def insert_document(self, doc, upsert=False):
        try:
            key = {"_id": doc['dados_basicos']['documento'][0]}
            result = self.documents.replace_one(key, doc, upsert=upsert)
            logger.debug(('save:', key))

            url_ = doc['geral_data']['url_base']+'/'+doc['geral_data']['session']+"/"
            url_ += doc['geral_data']['type_doc']+'?documento='+doc['geral_data']['num_doc']
            self._url.add_urls_day(url_)

        except DuplicateKeyError as e:
            print e
            logger.debug("move on - DuplicateKey")
        except KeyError:
            traceback.print_exc()
            logger.debug("move on")


class UrlManagerDao(MongoClient):

    def __init__(self, *args, **kwargs):
        super(UrlManagerDao, self).__init__(*args, **kwargs)
        self.db_urls = self.urls
        self.queue = self.db_urls.queue
        self.fallback = self.db_urls.fallback

    def add_urls_day(self, url):
        today = date.today()
        key = {"_id": today.strftime("%d/%m/%Y")}
        data = {
            "$addToSet": {
                "urls": url
            }
        }

        skip = False
        try:
            tmp = key
            tmp.update({"urls": [url]})
            result = self.queue.insert_one(tmp)
            skip = True
        except DuplicateKeyError as e:
            print str(e)
            logger.debug("Expected error - move on - DuplicateKey")

        if not skip:
            try:
                result = self.queue.update_one(key, data)
            except DuplicateKeyError as e:
                print e
                logger.debug("move on - DuplicateKey")
            except KeyError:
                traceback.print_exc()
                logger.debug("move on - add_urls_day")

    def set_chunk_url(self, list_url):
        date_ = date.today()
        key = {"_id": date_.strftime("%d/%m/%Y")}
        data = {
            "$addToSet": {
                "urls": {"$each": list_url}
            }
        }
        try:
            result = self.queue.update_one(key, data)
        except DuplicateKeyError as e:
            print e
            logger.debug("move on - DuplicateKey")
        except KeyError:
            traceback.print_exc()
            logger.debug("move on - Set_chunk_url")

