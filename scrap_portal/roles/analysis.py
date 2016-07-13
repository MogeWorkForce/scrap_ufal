# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import os
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

logger_data_analysis = logging.getLogger("Scrap_Ufal.data_analysis")
logger_data_analysis.setLevel(level_debug)

from ..data_model.dao.mongodb import DocumentsDao

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    docs_dao = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    docs_dao = DocumentsDao(host='172.17.0.1')


def analysis_bidding_mode():
    error_founded = defaultdict(dict)
    total_correct = 0
    total = 0
    total_error = 0
    for role in docs_dao.roles.find():
        type_bidding = role['_id']
        tipo_de_licitacao = role['tipo_de_licitacao']
        logger_data_analysis.debug('-' * 20)
        logger_data_analysis.debug('Type_bidding: %s', type_bidding)
        for doc in docs_dao.documents.find(json.loads(role['query'])):
            logger_data_analysis.debug(doc['_id'])
            mod_licitacao = doc['dados_detalhados']['modalidade_de_licitacao']
            if isinstance(mod_licitacao, (tuple, list)):
                mod_licitacao = mod_licitacao[0]

            error_this_doc = []
            limit_value = get_amount_empenhado(doc)
            logger_data_analysis.debug(mod_licitacao)
            logger_data_analysis.debug(doc['geral_data']['url'])

            if not mod_licitacao:
                logger_data_analysis.debug("Bidding mode not found!")

                error_this_doc.append({
                    'code': BIDDING_NOT_FOUND,
                    'error': VERBOSE_ERROR_TYPE[BIDDING_NOT_FOUND]
                })

            else:
                correct_bidding = get_correct_type_bidding(limit_value,
                                                           tipo_de_licitacao)
                correct_bidding = normalize_text(correct_bidding)
                if correct_bidding == normalize_text(type_bidding):
                    logger_data_analysis.debug("Correct bidding mode!")
                else:
                    logger_data_analysis.debug("Wrong bidding mode!")

                    error_this_doc.append({
                        'code': WRONG_BIDDING,
                        'error': VERBOSE_ERROR_TYPE[WRONG_BIDDING],
                        'correct': correct_bidding
                    })

            if check_exceded_amount(doc):
                error_this_doc.append({
                    'code': EXCEDED_LIMIT_OF_PAYMENTS,
                    'error': VERBOSE_ERROR_TYPE[EXCEDED_LIMIT_OF_PAYMENTS]
                })

            logger_data_analysis.debug('limite de gastos (%s): %.2f',
                                       doc['_id'], limit_value)
            if limit_value == 0:
                error_this_doc.append({
                    'code': NULL_VALUE_EMPENHADO,
                    'error': VERBOSE_ERROR_TYPE[NULL_VALUE_EMPENHADO]
                })

            if error_this_doc:
                error_founded[doc['_id']] = error_this_doc
                total_error += 1
            else:
                total_correct += 1

            total += 1

        logger_data_analysis.debug('-' * 20)
    logger_data_analysis.debug("We found this errors: %s",
                               json.dumps(error_founded))
    logger_data_analysis.debug("Total Correct: %s", total_correct)
    logger_data_analysis.debug("Total Analysed: %s", total)


def check_exceded_amount(doc):
    doc_ordered = order_by_date(doc['documentos_relacionados'])

    logger_data_analysis.debug('doc: %s', doc['_id'])
    limit_value = doc['dados_basicos']['valor']
    notas_pagamento = 0
    for item in doc_ordered:
        type_bidding_relational_docs = normalize_text(item['fase'])
        type_species_of_bidding = normalize_text(item['especie'])
        if type_bidding_relational_docs == 'pagamento':
            notas_pagamento += item['valor_rs']
        elif type_bidding_relational_docs == 'empenho':
            if type_species_of_bidding == 'anulacao':
                limit_value -= item['valor_rs']
            elif type_species_of_bidding == 'reforco':
                limit_value += item['valor_rs']

        if limit_value < notas_pagamento:
            return True

    return False


def get_amount_empenhado(doc):
    limit_value = doc['dados_basicos']['valor']
    for item in doc['documentos_relacionados']:
        type_bidding_relational_docs = normalize_text(item['fase'])
        type_species_of_bidding = normalize_text(item['especie'])
        if type_bidding_relational_docs == 'empenho':
            if type_species_of_bidding == 'anulacao':
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


if __name__ == "__main__":
    analysis_bidding_mode()
