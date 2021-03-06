# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import re
import time
from datetime import date, timedelta

import requests

from .scrap_request import get_any_proxy
from ..data_model.dao.mongodb import UrlManagerDao, ProxiesDao
from ..utils import clean_result

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'PROD':
    url_dao = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))
    proxy_dao = ProxiesDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    url_dao = UrlManagerDao(host='172.17.0.1')
    proxy_dao = ProxiesDao(host='172.17.0.1')

link_match = re.compile(r'a href="(?P<link_url>[^"]*)"?')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
get_paginator = re.compile(
    r'<span class="paginaXdeN">Página (?P<inicio>\d{1,3}?) de (?P<fim>\d{1,3})</span>')

logger = logging.getLogger("HBEM.pro_active")
level_debug = logging.DEBUG
logger.setLevel(level_debug)

fmt_data = "%d/%m/%Y"


def get_random_batch(batch_size=5):
    logger.debug("----- Start Random way to get a urls to feed a queue -----")
    today = date.today()
    pk_today = int(today.strftime(url_dao.PATTERN_PK))
    current_in_progress = url_dao.queue.find_one({"_id": pk_today})
    current_in_fallback = url_dao.fallback.find_one({"_id": pk_today})

    if current_in_progress and current_in_progress.get('urls'):
        return
    if current_in_fallback and current_in_fallback.get('urls'):
        return

    random_params = url_dao.random_finder_urls_notas(many_items=batch_size)
    for pay_load in random_params:
        key = pay_load.pop('_id')
        get_links_notas_empenho(**pay_load)
        url_dao.finder_urls_notas.remove({"_id": key})

    logger.debug("----- End Random way to get a urls to feed a queue -----")


def get_links_notas_empenho(date_start=None, date_end=None, params=None):
    url_base = "http://portaltransparencia.gov.br/despesasdiarias/"
    url = url_base + "resultado"

    if not date_start:
        date_start = date.today()

    if not date_end:
        date_end = date_start - timedelta(days=30)

    dates = [date_start, date_end]
    dates.sort()
    remain_days = (dates[0] - dates[1]).days
    tmp_date_end = dates[1]
    if remain_days > 30:
        dates[1] = date_start - timedelta(days=30)
        remain_days -= 30

    if not params:
        # Default will be search by "Pagamento" of UFAL
        params = {
            "fase": "PAG",
            "codigoOS": 26000,
            "codigoOrgao": 26231,
            "codigoUG": "TOD",
            "codigoED": "TOD",
            "codigoFavorecido": None,
            "consulta": "avancada"
        }

    params.update({
        "periodoInicio": dates[0].strftime(fmt_data),
        "periodoFim": dates[1].strftime(fmt_data),
    })

    _id, prx = get_any_proxy()
    try:
        result = requests.get(
            url, params=params, proxies=prx, timeout=10)
        tables = match.findall(clean_result(result))
        for content in tables:
            links = link_match.findall(content)
            links = [url_base + item for item in links]
            url_dao.set_chunk_url(links)

        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    _url_pg = result.url
    paginas = get_paginator.findall(clean_result(result))
    end_link_paginator = '&pagina=%s#paginacao'

    for pg in paginas[:1]:
        _, end = pg
        for next_pg in xrange(1, int(end) + 1):
            if next_pg == 1:
                continue
            else:
                link_ = _url_pg + end_link_paginator % next_pg

            logger.debug(link_)
            if "captcha" in link_:
                raise Exception("This thread on captcha page")
            time.sleep(4)
            _id, prx = get_any_proxy()
            try:
                result = requests.get(
                    link_, proxies=prx, timeout=10)
                tables = match.findall(clean_result(result))
                for content in tables:
                    links = link_match.findall(content)
                    links = [url_base + item for item in links]
                    url_dao.set_chunk_url(links)
                proxy_dao.mark_unused_proxy(_id)
            except Exception:
                proxy_dao.mark_unused_proxy(_id, error=True)
                raise

    logger.debug(result.url)
    if "captcha" in result.url:
        raise Exception("This thread on captcha page")

    if remain_days > 0:
        get_links_notas_empenho(date_start=dates[1], date_end=tmp_date_end)


if __name__ == "__main__":
    get_links_notas_empenho()
