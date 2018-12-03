# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import argparse
import logging
import os
import re
import time
import traceback
from datetime import date

import requests
from bs4 import BeautifulSoup

from ..data_model.dao.mongodb import DocumentsDao, ProxiesDao
from ..utils import clean_result, normalize_text, REMOVE_SPACES_REGEX

logger = logging.getLogger("HBEM.scraper")
level_debug = logging.DEBUG
logger.setLevel(level_debug)

base_data = re.compile(r'(?P<host>http?://.*?)/(?P<session>[^/]*)/'
                       r'(?P<type_doc>[^?]*)?.*?/(?P<num_doc>[a-zA-Z0-9]*)')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')
match_subtable = re.compile(r'<table class="subtabela">(.*?)<\/table>')
get_paginator = re.compile(
    r'<span class="paginaXdeN">Página (?P<inicio>\d{1,3}?) de (?P<fim>\d{1,3})</span>')

match_content = re.compile(
    r'<(?:t(?:d|h)|a|span)[^>]*?\s?(?:class="(?P<class>[^"]*?)")?.*?'
    r'(?:href="(?P<link_document>[^"]*?)")?>(?P<content>[^<]*?)</(?:t(?:d|h)|a|span)>'
)

match_tr = re.compile(
    r'<tr\s?(?:class="(?P<class_tr>[^"]*)")?.*?>(?P<content_tr>.*?)<\/tr>'
)

MODE = os.environ.get('MODE', 'DEV')
URL_RELATED_DOCUMENTS = "/despesas/documento/documentos-relacionados/resultado"
URL_EXPENSES_DETAIL = "/despesas/documento/{}/detalhamento/resultado"
URL_IMPACTED_EMPENHOS = "/despesas/documento/{}/empenhos-impactados/resultado"
URL_DESTINATION_BANKS = "/despesas/documento/{}/listaBancos/resultado"
URL_PAIED_INVOICES = "/despesas/documento/{}/listaFaturas/resultado"
URL_PAIED_PRECATORIOS = "/despesas/documento/{}/listaPrecatorios/resultado"

if MODE == 'PROD':
    client = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
    proxy_dao = ProxiesDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    client = DocumentsDao()
    proxy_dao = ProxiesDao()

start_ = time.time()


def get_any_proxy():
    proxy = proxy_dao.get_unused_proxy()
    key_ = proxy['proxy'].split('//')[0]
    proxies = {
        key_: proxy
    }
    return proxy['_id'], proxies


def save_or_update(doc):
    client.insert_document(doc, upsert=True)


def try_numeric(value):
    try:
        tmp_value = value.replace("R$", "").replace(".", "").replace(",", ".")
        value = float(tmp_value)
    except ValueError:
        pass
    return value


def get_general_data(url, data=None):
    if not data:
        data = {'geral_data': {}}
    if 'geral_data' not in data:
        data['geral_data'] = {}

    for dt in base_data.finditer(url):
        print(dt.groups())
        data['geral_data']['url_base'] = dt.group("host")
        data['geral_data']['type_doc'] = dt.group("type_doc")
        data['geral_data']['num_doc'] = dt.group("num_doc")
        data['geral_data']['session'] = dt.group("session")

    data['geral_data']['url'] = url
    return data


# TODO: pessimo nome, mudar isso depois
def cleaned_content(url, visited_links, proxy):
    time.sleep(4.1)
    logger.debug((len(visited_links), url))
    logger.debug(proxy)
    result = requests.get(url, timeout=10, proxies=proxy)
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

    _id, proxy = get_any_proxy()
    try:
        result = cleaned_content(url, visited_links, proxy)

        no_spaces = result
        data = load_content(no_spaces, paginator, data, visited_links)
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return data


def get_related_documents(data):
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "100",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "fase",
        "colunasSelecionadas": "data,fase,documentoResumido,especie",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543455305806"
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_RELATED_DOCUMENTS
    logger.info(url)
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("related_docs", response.url))
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return response.json()["data"]


def get_expenses_detail(data):
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "100",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "valorUnitario",
        "colunasSelecionadas": "subitem,quantidade,valorUnitario,valorTotal,descricao",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543460544120"
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_EXPENSES_DETAIL.format(
        data["geral_data"]["type_doc"]
    )
    logger.info(url)
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("expenses_details", response.url))
        tmp_data = response.json()["data"]
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        return []

    return tmp_data


def get_impacted_empenhos(data):
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "100",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "empenhoResumido",
        "colunasSelecionadas": "empenhoResumido,valorPago,valorRestoInscrito,"
                               "valorRestoCancelado,valorRestoPago",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543802606317"
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_IMPACTED_EMPENHOS.format(
        data["geral_data"]["type_doc"]
    )
    logger.info(url)
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("impacted_empenhos", response.url))
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return response.json()["data"]


def get_destination_banks(data):
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "15",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "nomeBanco",
        "colunasSelecionadas": "codigoLista,skBanco,nomeBanco,numeroAgencia,"
                               "valorLancamento",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543802606318"
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_DESTINATION_BANKS.format(
        data["geral_data"]["type_doc"]
    )
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("get_destination_banks", response.url))
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return response.json()["data"]


def get_paied_invoices(data):
    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "100",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "codigoSequencia",
        "colunasSelecionadas": "codigoLista,codigoSequencia,"
                               "codFavorecidoFormatado,nomFavorecido,"
                               "valorLancamento,valorDesconto,valorJuros,"
                               "valorDeducao,valorAcrescimo",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543802606319"
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_PAIED_INVOICES.format(
        data["geral_data"]["type_doc"]
    )
    logger.info(url)
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("get_paied_invoices", response.url))
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return response.json()["data"]


def get_paied_precatorios(data):

    querystring = {
        "paginacaoSimples": "true",
        "tamanhoPagina": "15",
        "offset": "0",
        "direcaoOrdenacao": "desc",
        "colunaOrdenacao": "valorPrecatorio",
        "colunasSelecionadas": "codigoLista,numeroParcela,valorPrecatorio",
        "fase": data["dados_basicos"]["fase"],
        "codigo": data["geral_data"]["num_doc"],
        "_": "1543802606320"
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = data["geral_data"]["url_base"] + URL_PAIED_PRECATORIOS.format(
        data["geral_data"]["type_doc"]
    )
    logger.info(url)
    _id, proxy = get_any_proxy()
    try:
        response = requests.get(
            url, headers=headers, params=querystring, proxies=proxy)
        logger.info(("get_paied_precatorios", response.url))
        proxy_dao.mark_unused_proxy(_id)
    except Exception:
        proxy_dao.mark_unused_proxy(_id, error=True)
        raise

    return response.json()["data"]


def load_content(content_original, paginator=False, data=None,
                 visited_links=None):
    if not visited_links:
        visited_links = []

    if not data:
        data = {}

    logger.info("Start get data from")
    parser = BeautifulSoup(content_original, 'html.parser')
    target_classes = ["dados-tabelados", "dados-detalhados"]
    for table_content in parser.find_all("section", class_=target_classes):
        class_section = table_content["class"][0]
        if class_section == 'dados-tabelados':
            key_parent = "dados_basicos"
        else:
            key_parent = "".join([
                x.string.strip() for x in
                table_content.button.contents if x.string])
            key_parent = normalize_text(key_parent)
        # print(key_parent)
        data[key_parent] = {}

        for sub_content in table_content.find_all("div", class_='col-xs-12'):
            try:
                key = sub_content.strong.string
                key = normalize_text(key)
                value = " ".join([
                    x.string.strip() for x in sub_content.find_all("span")
                    if x.string
                ]).replace("\t", " ")
                if not value:
                    value = "".join([
                        x.string.strip() for x in sub_content.find_all("a")
                        if x.string
                    ]).replace("\t", " ")
                value = REMOVE_SPACES_REGEX.sub(" ", value)
                data[key_parent][key] = try_numeric(value)
            except:
                print("Falha na key", key)

    data["documentos_relacionados"] = get_related_documents(data)
    data["detalhamento_do_gasto"] = get_expenses_detail(data)

    if data["geral_data"]["type_doc"] in ["pagamento", "liquidacao"]:
        data["empenhos_impactados"] = get_impacted_empenhos(data)

    if data["geral_data"]["type_doc"] == "pagamento":
        data["bancos_destinatarios"] = get_destination_banks(data)
        data["faturas_pagas"] = get_paied_invoices(data)
        data["precatorios_pagos"] = get_paied_precatorios(data)

    related_docs_links = [
        "{}/{}/{}/{}?ordenarPor=fase&direcao=desc".format(
            data["geral_data"]["url_base"],
            data["geral_data"]["session"],
            doc["fase"].lower(),
            doc["documento"],
        ) for doc in data["documentos_relacionados"]
    ]
    # print(related_docs_links)
    save_or_update(data)

    client.url.set_chunk_url(related_docs_links)
    return data


def load_url_from_queue(batch=1, collection='queue'):
    try:
        import random
        logger.debug('----- start new job! (%s) Batches: %s',
                     collection.upper(), batch)
        date_ = date.today()
        key = {"_id": int(date_.strftime(client.url.PATTERN_PK))}
        urls_load = client.url.db_urls[collection].find_one(key)

        length_urls = len(urls_load['urls'])

        if length_urls <= 0:
            logger.warn(
                "(%s) Finish the Process all Urls", collection.upper())
            return
        elif length_urls == 1:
            init_ = 0
        else:
            init_ = random.randint(0, length_urls + 1)
            if init_ + batch >= length_urls:
                init_ -= batch
                init_ = init_ if init_ > 0 else 0

        logger.debug(
            "(%s) Interval %s to %s", collection.upper(), init_, init_ + batch)
        tmp_urls_load = urls_load['urls'][init_:init_ + batch]

        for url in tmp_urls_load:
            try:
                in_ = client.url.verify_today_urls(url)

                if not in_:
                    logger.debug('Start load url_from %s! %s',
                                 collection.upper(), url)
                    get_content_page(url)
                    client.url.dynamic_url('queue_loaded', url)
                else:
                    logger.warn("Url already loaded: %s", url)
            except:
                traceback.print_exc()
                client.url.dynamic_url('fallback', url)
                logger.warn("Call Fallback to Url: %s", url)

        try:
            client.url.remove_urls(tmp_urls_load, collection=collection)
            logger.debug('(%s)Pass to remove_urls! Batches: %d',
                         collection.upper(), batch)
        except Exception as e:
            traceback.print_exc()
            logger.warn("Error on remove urls")

    except:
        traceback.print_exc()
        logger.debug('Errors on %s!', collection.upper())
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

    print('finish in: ', time.time() - start_)
