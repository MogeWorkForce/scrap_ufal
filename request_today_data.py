# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from data_model.dao.mongodb import UrlManagerDao
import requests
from datetime import date, timedelta
import logging
import re
import os

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'DEV':
    client = UrlManagerDao()
elif MODE == "DOCKER":
    client = UrlManagerDao(host='172.17.0.1')
else:
    client = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))

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


def main(date_start=None, before=False, time_elapse=15):
    url_base = "http://portaltransparencia.gov.br/despesasdiarias/"
    url = url_base + "resultado"

    elapse = timedelta(days=time_elapse)

    if not date_start:
        date_start = date.today()

    datas = [date_start,
             date_start - elapse if not before else date_start + elapse]

    datas.sort()
    print datas

    params = {
        "periodoInicio": datas[0].strftime(fmt_data),
        "periodoFim": datas[1].strftime(fmt_data),
        "fase": "PAG",
        "codigoOS": 26000,
        "codigoOrgao": 26231,
        "codigoUG": "TOD",
        "codigoED": "TOD",
        "codigoFavorecido": None,
        "consulta": "avancada"
    }

    result = requests.get(url, params=params)
    tables = match.findall(clean_result(result))
    for content in tables:
        links = link_match.findall(content)
        links = [url_base + item for item in links]
        client.set_chunk_url(links)

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

            result = requests.get(link_)
            tables = match.findall(clean_result(result))
            for content in tables:
                links = link_match.findall(content)
                links = [url_base + item for item in links]
                client.set_chunk_url(links)

    print result.url


if __name__ == "__main__":
    main()
