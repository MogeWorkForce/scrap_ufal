# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from pymongo.errors import DuplicateKeyError
from ..data_model.dao.mongodb import DocumentsDao

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    docs_dao = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    # docs_dao = DocumentsDao(host='172.17.0.1')
    docs_dao = DocumentsDao()

def insert_roles():

    roles = [
        {
            u'query': u'{"dados_detalhados.elemento_de_despesa": "51 - OBRAS E INSTALACOES", "dados_detalhados.categoria_de_despesa": "4 - Despesas de Capital", "dados_basicos.especie_de_empenho": "Original", "dados_basicos.valor": {"$lte": 150000, "$gte": 15000.01}}',
            u'_id': u'convite',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            u'query': u'{"dados_detalhados.elemento_de_despesa": "51 - OBRAS E INSTALACOES", "dados_detalhados.categoria_de_despesa": "4 - Despesas de Capital", "dados_basicos.especie_de_empenho": "Original", "dados_basicos.valor": {"$lte": 1500000, "$gte": 150000.01}}',
            u'_id': u'tomada de preços',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            u'query': u'{"dados_detalhados.elemento_de_despesa": "51 - OBRAS E INSTALACOES", "dados_detalhados.categoria_de_despesa": "4 - Despesas de Capital", "dados_basicos.especie_de_empenho": "Original", "dados_basicos.valor": {"$gte": 1500000}}',
            u'_id': u'concorrência',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            u'query': u'{"dados_detalhados.elemento_de_despesa": "51 - OBRAS E INSTALACOES", "dados_detalhados.categoria_de_despesa": "4 - Despesas de Capital", "dados_basicos.especie_de_empenho": "Original", "dados_basicos.valor": {"$lte": 15000}}',
            u'_id': u'dispensa',
            'tipo_de_licitacao': 'engenharia'
        }
    ]

    bidding_mode = [
        {
            'max': 15000, 'min': 0,
            '_id': u'dispensa',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            'max': 150000, 'min': 15000.01,
            u'_id': u'convite',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            'max': 1500000, 'min': 150000.01,
            u'_id': u'tomada de preços',
            'tipo_de_licitacao': 'engenharia'
        },
        {
            'min': 1500000,
            u'_id': u'concorrência',
            'tipo_de_licitacao': 'engenharia'
        },
    ]

    for role in roles:
        try:
            docs_dao.roles.insert(role)
        except DuplicateKeyError:
            pass

    for bd_md in bidding_mode:
        try:
            docs_dao.bidding_mode.insert(bd_md)
        except DuplicateKeyError:
            pass


if __name__ == "__main__":
    insert_roles()
