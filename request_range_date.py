# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import requests
import logging
import os
import random
import re

from datetime import date, timedelta
from data_model.dao.mongodb import UrlManagerDao, ProxiesDao
from scrap_request import get_any_proxy

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'DEV':
    url_dao = UrlManagerDao()
    proxy_dao = ProxiesDao()
elif MODE == "DOCKER":
    url_dao = UrlManagerDao(host='172.17.0.1')
    proxy_dao = ProxiesDao(host='172.17.0.1')
else:
    url_dao = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))
    proxy_dao = ProxiesDao(os.environ.get('MONGODB_ADDON_URI'))

link_match = re.compile(r'a href="(?P<link_url>[^"]*)"?')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
get_paginator = re.compile(
    r'<span class="paginaXdeN">Página (?P<inicio>\d{1,3}?) de (?P<fim>\d{1,3})</span>')
formatter = logging.Formatter(
    "[%(name)s][%(levelname)s][PID %(process)d][%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("Scrap_Ufal")
level_debug = logging.DEBUG
logger.setLevel(level_debug)
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

log_proactive = logging.getLogger("Scrap_Ufal.pro_active")
log_proactive.setLevel(level_debug)

fmt_data = "%d/%m/%Y"


def clean_result(result):
    return result.text.replace('\n', '').replace(
        '  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')


def get_random_batch(batch_size=5):
    logger.debug("----- Start Random way to get a urls to feed a queue -----")
    for _ in xrange(batch_size):
        pay_load = url_dao.random_finder_urls_notas()
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
    remain_days = dates[0] - dates[1]
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }
        result = requests.get(url, params=params, headers=headers, proxies=prx)
        tables = match.findall(clean_result(result))
        for content in tables:
            links = link_match.findall(content)
            links = [url_base + item for item in links]
            url_dao.set_chunk_url(links)

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

                result = requests.get(link_, headers=headers, proxies=prx)
                tables = match.findall(clean_result(result))
                for content in tables:
                    links = link_match.findall(content)
                    links = [url_base + item for item in links]
                    url_dao.set_chunk_url(links)

        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id)
        raise

    logger.debug(result.url)

    if remain_days >= 1:
        get_links_notas_empenho(date_start=dates[1], date_end=tmp_date_end)


if __name__ == "__main__":
    get_links_notas_empenho()
