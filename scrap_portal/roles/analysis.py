# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import os
import traceback
from collections import defaultdict

from ..utils import normalize_text
from ..utils.analysis_codes import NULL_VALUE_EMPENHADO, BIDDING_NOT_FOUND
from ..utils.analysis_codes import VERBOSE_ERROR_TYPE
from ..utils.analysis_codes import WRONG_BIDDING, EXCEDED_LIMIT_OF_PAYMENTS

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

logger_analysis = logging.getLogger("Scrap_Ufal.data_analysis")
logger_analysis.setLevel(level_debug)

from ..data_model.dao.mongodb import DocumentsDao

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    docs_dao = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    docs_dao = DocumentsDao(host='172.17.0.1')

pattern_url = "http://portaltransparencia.gov.br/despesasdiarias/pagamento?documento=%s%s%s"


def analysis_bidding_mode():
    error_founded = defaultdict(dict)
    correct_founded = defaultdict(dict)
    total_correct = 0
    total = 0
    total_error = 0
    for role in docs_dao.roles.find():
        type_bidding = role['_id']
        logger_analysis.debug('-' * 20)
        logger_analysis.debug(
            'Provável Modalidade de Licitação, baseada no valor empenhado: %s',
            type_bidding)
        correct_bidding = normalize_text(type_bidding)
        for doc in docs_dao.documents.find(json.loads(role['query'])):
            logger_analysis.debug(doc['_id'])
            mod_licitacao = doc['dados_detalhados']['modalidade_de_licitacao']
            if isinstance(mod_licitacao, (tuple, list)):
                mod_licitacao = mod_licitacao[0]

            error_this_doc = []
            limit_value = get_amount_empenhado(doc)
            logger_analysis.debug(mod_licitacao)
            logger_analysis.debug(doc['geral_data']['url'])

            if not mod_licitacao:
                logger_analysis.debug("Modalide de Licitação não Encontrada.")

                error_this_doc.append({
                    'code': BIDDING_NOT_FOUND,
                    'error': VERBOSE_ERROR_TYPE[BIDDING_NOT_FOUND]
                })

            elif correct_bidding == normalize_text(mod_licitacao):
                logger_analysis.debug("Modalidade de Licitação Correta!")
            else:
                logger_analysis.debug("Modalidade de Licitação Errada!")

                error_this_doc.append({
                    'code': WRONG_BIDDING,
                    'error': VERBOSE_ERROR_TYPE[WRONG_BIDDING],
                    'correct': correct_bidding
                })

            if check_exceded_amount(doc):
                error_msg = VERBOSE_ERROR_TYPE[EXCEDED_LIMIT_OF_PAYMENTS]
                logger_analysis.debug(error_msg)
                error_this_doc.append({
                    'code': EXCEDED_LIMIT_OF_PAYMENTS,
                    'error': error_msg
                })

            logger_analysis.debug('limite de gastos (%s): %.2f',
                                  doc['_id'], limit_value)
            if limit_value <= 0:
                error_msg = VERBOSE_ERROR_TYPE[NULL_VALUE_EMPENHADO]
                logger_analysis.debug(error_msg)
                error_this_doc.append({
                    'code': NULL_VALUE_EMPENHADO,
                    'error': error_msg
                })

            if error_this_doc:
                error_founded[doc['_id']] = error_this_doc
                total_error += 1
            else:
                correct_founded[doc['_id']] = doc['geral_data']['url']
                total_correct += 1

            total += 1

        logger_analysis.debug('-' * 20)
    logger_analysis.debug("Erros Encontrados: %s",
                          json.dumps(error_founded, indent=2))
    logger_analysis.debug("Total Certas: %s", total_correct)
    logger_analysis.debug("Total com Erros: %s", total_error)
    logger_analysis.debug("Total Analisadas: %s", total)
    logger_analysis.debug("Corretas Encontrados: %s",
                          json.dumps(correct_founded, indent=2))


def check_exceded_amount(doc):
    doc_id = doc['_id']
    basic_data = doc['dados_basicos']
    doc_ordered = order_by_date(doc['documentos_relacionados'])

    logger_analysis.debug('doc: %s', doc['_id'])
    limit_value = doc['dados_basicos']['valor']
    notas_pagamento = 0
    for item in doc_ordered:
        type_bidding_relational_docs = normalize_text(item['fase'])
        type_species_of_bidding = normalize_text(item['especie'])
        if type_bidding_relational_docs == 'pagamento':
            logger_analysis.debug('--- %s', item['documento'])
            if 'OB' not in item['documento']:
                notas_pagamento += item['valor_rs']
            else:
                logger_analysis.debug(
                    "Check se já está indexado ou colocar a url na QUEUE, para "
                    "ser recuperado e processado o conteúdo: %s",
                    item['documento'])
                payment_in_analyses = docs_dao.documents.find_one({
                    "_id": item['documento']
                })
                if payment_in_analyses:
                    notas_pagamento += retrieve_payment_by_empenho(
                        payment_in_analyses, doc_id)
                else:
                    logger_analysis.debug(
                        "Coloque essa url na QUEUE para ser para ter seus dados"
                        " coletados no futuro.")

                    value = item['valor_rs']
                    logger_analysis.debug(item['especie'])
                    if 'OBS ' in item['especie']:
                        logger_analysis.debug(
                            'Encontrado "OBS" (Tipo de Ordem Bancaria) dentro '
                            'da coluna Espécie. Valor será subtraído.')
                        value *= -1

                    notas_pagamento += item['valor_rs']
                    unidade_gestora_emitente = get_only_numbers(
                        basic_data['unidade_gestora_emitente'])
                    gestao = get_only_numbers(basic_data['gestao'])
                    url = pattern_url % (
                        unidade_gestora_emitente, gestao, item['documento'])
                    logger_analysis.debug('url: "%s"', url)
                    docs_dao.url.dynamic_url('queue', url)

        elif type_bidding_relational_docs == 'empenho':
            if type_species_of_bidding in ['anulacao', 'cancelamento']:
                limit_value -= item['valor_rs']
            elif type_species_of_bidding == 'reforco':
                limit_value += item['valor_rs']
        logger_analysis.debug("(%s) limite: %.2f ---- pagamento: %.2f",
                              item['data'], limit_value, notas_pagamento)
        if round(notas_pagamento, 2) > round(limit_value, 2):
            return True

    return False


def get_amount_empenhado(doc):
    limit_value = doc['dados_basicos']['valor']
    for item in doc['documentos_relacionados']:
        type_bidding_relational_docs = normalize_text(item['fase'])
        type_species_of_bidding = normalize_text(item['especie'])
        if type_bidding_relational_docs == 'empenho':
            if type_species_of_bidding in ['anulacao', 'cancelamento']:
                limit_value -= item['valor_rs']
            elif type_species_of_bidding == 'reforco':
                limit_value += item['valor_rs']

    return limit_value


def get_correct_type_bidding(value, tipo_de_licitacao):
    type_bidding = docs_dao.bidding_mode.find({
        "tipo_de_licitacao": tipo_de_licitacao,
        "min": {"$lte": value}
    }, sort=[("min", -1)], limit=1)

    type_bidding = list(type_bidding)[0]['_id']
    return type_bidding


def order_by_date(list_item):
    indexes = [(item['data'], i) for i, item in enumerate(list_item)]
    indexes.sort()
    new_list_item = []
    for _, index in indexes:
        new_list_item.append(list_item[index])
    return new_list_item


def retrieve_payment_by_empenho(nota_pagamento, doc_empenho_id):
    try:
        value = 0
        cancel_purge = 'nao'
        data_details = nota_pagamento['dados_detalhados']
        documents_detail = data_details['detalhamento_do_documento']
        if isinstance(documents_detail['empenho'], list):
            index_empenho = documents_detail['empenho'].index(doc_empenho_id)
            value = documents_detail['valor_rs'][index_empenho]
            cancel_purge = normalize_text(
                documents_detail['cancelamento_estorno'][index_empenho])

        elif documents_detail['empenho'] == doc_empenho_id:
            value = documents_detail['valor_rs']
            cancel_purge = normalize_text(
                documents_detail['cancelamento_estorno'])

        if cancel_purge == 'sim':
            value *= -1  # Se estorno/cancelamento, o valor será decrementado
        return value
    except ValueError:
        traceback.print_exc()
        return 0


def get_only_numbers(word):
    return word.split('-')[0].strip()


if __name__ == "__main__":
    analysis_bidding_mode()
