# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os

from datetime import date, timedelta

from ..utils import level_debug
from ..data_model.dao.mongodb import UrlManagerDao


logger = logging.getLogger("Scrap_Ufal.maintance")
logger.setLevel(level_debug)

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    url_dao = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    url_dao = UrlManagerDao(host='172.17.0.1')


def get_unique_urls(collection='queue_loaded'):
    """
    get unique urls in one collection, and put then in current day
    :param collection: str
    :return: None
    """
    now = date.today()
    number_days = os.environ.get('DAYS_BEFORE', 7)
    min_day_get_urls = now - timedelta(days=int(number_days))
    query = {
        "_id": {
            "$gte": min_day_get_urls.strftime(url_dao.PATTERN_PK),
            "$lt": now.strftime(url_dao.PATTERN_PK)
        }
    }
    for url in url_dao.db_urls[collection].find(query):
        url_dao.set_chunk_url(url['urls'], collection)

    many_days_erased = url_dao.db_urls[collection].delete_many(query)
    logger.debug(
        'How many days are dropped: %d', many_days_erased.deleted_count)
