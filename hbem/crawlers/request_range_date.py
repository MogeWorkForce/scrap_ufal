# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
import time
from datetime import date

import requests

from .scrap_request import get_any_proxy
from ..data_model.dao.mongodb import UrlManagerDao, ProxiesDao
from ..utils import normalize_text

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'PROD':
    url_dao = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))
    proxy_dao = ProxiesDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    url_dao = UrlManagerDao()
    proxy_dao = ProxiesDao()

logger = logging.getLogger("HBEM.pro_active")
level_debug = logging.INFO
logger.setLevel(level_debug)

fmt_data = "%d/%m/%Y"


def get_links_notas_empenho(date_=None):
    if not date_:
        date_ = date.today()

    url = "http://portaltransparencia.gov.br/despesas/favorecido/resultado"
    page_length = 1000
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": page_length,
        "offset": 0,
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "valor",
        "colunasSelecionadas": "data,documentoResumido,localizadorGasto,fase,"
                               "especie,favorecido,ufFavorecido,valor,ug,uo,"
                               "orgao,orgaoSuperior,grupo,elemento,modalidade",
        "de": date_.strftime(fmt_data),
        "ate": date_.strftime(fmt_data),
        "faseDespesa": "3",  # 1 = Empenho, 2 = Liquidação, 3 = Pagamento
        "elemento": 51,
        "_": "1544146928896"
    }

    _id, prx = get_any_proxy()
    counter = 0
    while True:
        logger.info("-" * 30)
        try:
            logger.info("Offset current: %d", querystring["offset"])
            response = requests.request(
                "GET", url, params=querystring, proxies=prx, timeout=10)
            logger.info(response.url)
            data = response.json()

            related_docs_links = [
                "{}/{}/{}/{}?ordenarPor=fase&direcao=desc".format(
                    "http://portaltransparencia.gov.br",
                    "despesas",
                    normalize_text(doc["fase"]).lower(),
                    doc["documento"],
                ) for doc in data["data"]
            ]
            url_dao.set_chunk_url(related_docs_links)
            logger.info("recordsTotal: %d", data["recordsTotal"])
            if data["recordsTotal"] != 9223372036854775807:
                break
            querystring["offset"] += page_length

            counter += 1
            # reset counter when use same proxy more than 15 times
            if counter > 15:
                proxy_dao.mark_unused_proxy(_id)
                counter = 0
        except Exception:
            proxy_dao.mark_unused_proxy(_id, error=True)
            raise
        logger.info("-" * 30)
        time.sleep(1)


if __name__ == "__main__":
    print("entrou no main")
    get_links_notas_empenho(date(2018, 12, 10))
