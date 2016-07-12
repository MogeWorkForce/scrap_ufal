# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import os
from collections import defaultdict

from utils import normalize_text

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

from data_model.dao.mongodb import DocumentsDao

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    docs_dao = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    # docs_dao = DocumentsDao(host='172.17.0.1')
    docs_dao = DocumentsDao()

NULL_VALEU_EMPENHADO = 11
BIDDING_NOT_FOUND = 22
WRONG_BIDDING = 23


ERROR_TYPE = {
    BIDDING_NOT_FOUND: "Bidding mode not found",
    WRONG_BIDDING: "Wrong bidding mode",
    NULL_VALEU_EMPENHADO: "'Nota de Empenho' with 0 value after check limit."
}


def analysis_bidding_mode():
    # 0 - carregar as regras
    # 1 - Selecionar a nota de empenho de acordo com as regras
    # 2 - Checkar se a modalidade é consistente com a faixa de valores

    error_founded = defaultdict(dict)
    for role in docs_dao.roles.find():
        type_bidding = role['_id']
        logger_data_analysis.debug('-' * 20)
        logger_data_analysis.debug('Type_bidding: %s', type_bidding)
        for doc in docs_dao.documents.find(json.loads(role['query'])).limit(5):
            logger_data_analysis.debug(doc['_id'])
            mod_licitacao = doc['dados_detalhados']['modalidade_de_licitacao']
            if isinstance(mod_licitacao, (tuple, list)):
                mod_licitacao = mod_licitacao[0]

            error_this_doc = []
            logger_data_analysis.debug(mod_licitacao)
            logger_data_analysis.debug(doc['geral_data']['url'])

            if normalize_text(mod_licitacao) == normalize_text(type_bidding):
                logger_data_analysis.debug("Correct bidding mode!")
            elif not mod_licitacao:
                logger_data_analysis.debug("Bidding mode not found!")

                error_this_doc.append({
                    'code': BIDDING_NOT_FOUND,
                    'error': ERROR_TYPE[BIDDING_NOT_FOUND]
                })

            else:
                logger_data_analysis.debug("Wrong bidding mode!")
                logger_data_analysis.debug("Search if this 'nota de empenho' "
                                           "have another 'Reforço'")
                if check_extrapolar_amount(doc):
                    error_this_doc.append({
                        'code': WRONG_BIDDING,
                        'error': ERROR_TYPE[WRONG_BIDDING]
                    })

                limit_value = get_amount_empenhado(doc)
                logger_data_analysis.debug('limite de gastos: %.2f', limit_value)

            if error_this_doc:
                error_founded[type_bidding][doc['_id']] = error_this_doc

        logger_data_analysis.debug('-' * 20)
    logger_data_analysis.debug("We found this errors: %s",
                               json.dumps(error_founded))


def check_extrapolar_amount(doc):
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

        msg = '\n%s --- limit_value %s - notas_pagamento %s'
        logger_data_analysis.debug(msg,
                                   item['data'], limit_value, notas_pagamento)
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


def get_correct_type_bidding(value, actual_bidding_mode):
    pass


def order_by_date(list_item):
    indexes = [(item['data'], i) for i, item in enumerate(list_item)]
    indexes.sort()
    new_list_item = []
    for _, index in indexes:
        new_list_item.append(list_item[index])
    return new_list_item


if __name__ == "__main__":
    analysis_bidding_mode()
