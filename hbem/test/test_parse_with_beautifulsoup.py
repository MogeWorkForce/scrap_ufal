# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

import mock

from ..crawlers.scrap_request import load_content, DocumentsDao, clean_result

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DocumentsDao.insert_document = mock.MagicMock(return_value='')


def test_parse_data():
    expected = {u'dados_basicos': {u'favorecido': [
        u'03.486.715/0001-94- IMPRECAR COMERCIO E SERVICOS LTDA'],
                                   u'tipo_de_ob': [
                                       u'OBC PARA TERCEIROS NO MESMO BANCO'],
                                   u'valor': [u'R$ 30.705,05'],
                                   u'tipo_de_documento': [
                                       u'Ordem Banc\xe1ria (OB)'], u'gestao': [
            u'15222 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
                                   u'unidade_gestora_emitente': [
                                       u'153037 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
                                   u'orgao_entidade_vinculada': [
                                       u'26231 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
                                   u'orgao_superior': [
                                       u'26000 - MINISTERIO DA EDUCACAO'],
                                   u'fase': [u'Pagamento'],
                                   u'data': [u'02/09/2015'],
                                   u'documento': [u'2015OB807523']},
                u'documentos_relacionados': {
                    u'favorecido': [u'IMPRECAR COMERCIO E SERVICOS LTDA'],
                    u'especie': [u'Original'],
                    u'unidade_gestora': [u'UNIVERSIDADE FEDERAL DE ALAGOAS'],
                    u'elemento_de_despesa': [
                        u'OUTROS SERVICOS DE TERCEIROS-PESSOA JURIDICA'],
                    u'orgao_entidade_vinculada': [
                        u'UNIVERSIDADE FEDERAL DE ALAGOAS'],
                    u'orgao_superior': [u'MINISTERIO DA EDUCACAO'],
                    u'fase': [u'Empenho'], u'data': [u'09/02/2015'],
                    u'valor_rs': [u'1,00'], u'documento': [u'2015NE800115']},
                u'geral_data': {u'num_doc': u'153037152222015OB807523',
                                u'url': u'http://portaltransparencia.gov.br/despesasdiarias/pagamento?documento=153037152222015OB807523',
                                u'session': u'despesasdiarias',
                                u'url_base': u'http://portaltransparencia.gov.br',
                                u'type_doc': u'pagamento'},
                u'dados_detalhados': {u'modalidade_de_aplicacao': [
                    u'90 - Aplic. Diretas(Gastos Diretos do Governo Federal)'],
                                      u'processo_no': [u'23065.016725/2015-55'],
                                      u'grupo_de_despesa': [
                                          u'3- Outras Despesas Correntes'],
                                      u'categoria_de_despesa': [
                                          u'3- Despesas Correntes'],
                                      u'elemento_de_despesa': [
                                          u'39 - OUTROS SERVICOS DE TERCEIROS-PESSOA JURIDICA'],
                                      u'observacao_do_documento': [
                                          u'PAGAMENTO DE NFS-E 119 REF A 10 MEDI\xc7\xc3O DOS SERVI\xc7OS DE MANUTEN\xc7\xc3O CORRETIVA E REPARA\xc7\xc3O DOS EQUIPAMENTOS E INSTALA\xc7OES CONTRATO 47/2014, DA IMPRECAR COMERCIO E SERVICOS LTDA. PROCESSO.23065.016725/2015-55.'],
                                      u'detalhamento_do_documento': {
                                          u'valor_rs': [u'30.705,05'],
                                          u'cancelamento_estorno': [u'N\xe3o'],
                                          u'empenho': [u'2015NE800115'],
                                          u'subitem_da_despesa': [
                                              u'16 - MANUTENCAO E CONSERV. DE BENS IMOVEIS'],
                                          u'convenio_outros': [0.0]}}}

    html = open(BASE_DIR + '/base.html').read()
    provider_html = mock.Mock()
    provider_html.text = html.decode(encoding='utf-8')
    html = clean_result(provider_html)
    data = {
        u'geral_data': {
            u'num_doc': u'153037152222015OB807523',
            u'session': u'despesasdiarias',
            u'type_doc': u'pagamento',
            u'url': u'http://portaltransparencia.gov.br/despesasdiarias/pagamento?documento=153037152222015OB807523',
            u'url_base': u'http://portaltransparencia.gov.br'}
    }
    loaded_data = load_content(html, data=data)

    assert loaded_data == expected
