# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import logging
import os

from collections import defaultdict

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
    docs_dao = DocumentsDao(host='172.17.0.1')


def wrong_bidding_mode():
    # 0 - carregar as regras
    # 1 - Selecionar a nota de empenho de acordo com as regras
    # 2 - Checkar se a modalidade é consistente com a faixa de valores

    error_founded = defaultdict(dict)
    for role in docs_dao.roles.find():
        type_bidding = role['_id']
        logger_data_analysis.debug('-' * 20)
        logger_data_analysis.debug(type_bidding)
        for doc in docs_dao.documents.find(json.loads(role['query'])).limit(5):
            logger_data_analysis.debug(doc['_id'])
            mod_licitacao = doc['dados_detalhados']['modalidade_de_licitacao']
            if isinstance(mod_licitacao, (tuple, list)):
                mod_licitacao = mod_licitacao[0]

            logger_data_analysis.debug(mod_licitacao)
            logger_data_analysis.debug(doc['geral_data']['url'])

            if mod_licitacao.lower() == type_bidding:
                logger_data_analysis.debug("Correct bidding mode!")
            elif not mod_licitacao:
                logger_data_analysis.debug("Bidding mode not found!")
            else:
                logger_data_analysis.debug("Wrong bidding mode!")
                logger_data_analysis.debug("Search if this 'nota de empenho' "
                                           "have another 'Reforço'")

        logger_data_analysis.debug('-' * 20)
    logger_data_analysis.debug("We found this errors: %s",
                               json.dumps(error_founded))
if __name__ == "__main__":
    wrong_bidding_mode()
