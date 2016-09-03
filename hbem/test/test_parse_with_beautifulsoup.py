# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import time

import mock
import requests

from ..crawlers.scrap_request import load_content, DocumentsDao, clean_result
from ..data_model.dao.mongodb import UrlManagerDao, ProxiesDao

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DocumentsDao.insert_document = mock.MagicMock(return_value='')
UrlManagerDao.set_chunk_url = mock.MagicMock(return_value='')
dict_proxy = {
    "_id": "578580f05fbe7a42ad32018c",
    "last_date_in_use": 20160714011710,
    "localization": "Brazil Proxy Brazil",
    "proxy": "http://187.84.187.4:80",
    "in_use": False
}
ProxiesDao.get_unused_proxy = mock.MagicMock(return_value=dict_proxy)
ProxiesDao.mark_unused_proxy = mock.MagicMock(return_value='')

page_2 = open(BASE_DIR + '/page2.html').read()
provider_html_page2 = mock.Mock()
provider_html_page2.text = page_2.decode(encoding='utf-8')

requests.get = mock.MagicMock(return_value=provider_html_page2)
time.sleep = mock.MagicMock(return_value="")


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

    expected = {u'dados_basicos': {
        u'favorecido': [u'15303715222\t- UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'fase': [u'Empenho'], u'valor': [u'R$ 1,00'],
        u'tipo_de_documento': [u'Nota de Empenho (NE)'],
        u'gestao': [u'15222 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'unidade_gestora_emitente': [
            u'153037 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'tipo_de_empenho': [u'ESTIMATIVO'], u'orgao_entidade_vinculada': [
            u'26231 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'orgao_superior': [u'26000 - MINISTERIO DA EDUCACAO'],
        u'documento': [u'2011NE000224'], u'data': [u'01/02/2011'],
        u'especie_de_empenho': [u'Original']}, u'documentos_relacionados': {
        u'favorecido': [u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                        u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                        u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA',
                        u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA', u'BANCO DO BRASIL SA',
                        u'BANCO DO BRASIL SA'],
        u'especie': [u'Refor\xe7o', u'Anula\xe7\xe3o', u'Refor\xe7o',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA',
                     u'OBB PARA MESMO BANCO/AGENCIA', u'Refor\xe7o', u'', u'',
                     u'', u'', u'', u'', u'', u'', u'', u'', u''],
        u'unidade_gestora': [u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                             u'UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'elemento_de_despesa': [
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica',
            u'Outros Servi\xe7os de Terceiros - Pessoa F\xedsica'],
        u'orgao_entidade_vinculada': [u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS',
                                      u'UNIVERSIDADE FEDERAL DE ALAGOAS'],
        u'orgao_superior': [u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO',
                            u'MINISTERIO DA EDUCACAO'],
        u'fase': [u'Empenho', u'Empenho', u'Empenho', u'Pagamento',
                  u'Pagamento', u'Pagamento', u'Pagamento', u'Pagamento',
                  u'Pagamento', u'Pagamento', u'Empenho', u'Liquida\xe7\xe3o',
                  u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o',
                  u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o',
                  u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o', u'Liquida\xe7\xe3o',
                  u'Liquida\xe7\xe3o'],
        u'data': [u'04/02/2011', u'15/08/2011', u'01/08/2011', u'16/06/2011',
                  u'12/07/2011', u'27/05/2011', u'12/07/2011', u'16/06/2011',
                  u'27/05/2011', u'03/10/2011', u'30/09/2011', u'03/10/2011',
                  u'12/07/2011', u'12/07/2011', u'16/06/2011', u'',
                  u'16/06/2011', u'16/06/2011', u'16/06/2011', u'16/06/2011',
                  u'16/06/2011', u'24/05/2011', u'24/05/2011'],
        u'valor_rs': [u'25.500,00', u'14.401,00', u'11.400,00', u'9.300,00',
                      u'8.700,00', u'2.700,00', u'1.200,00', u'900,00',
                      u'900,00', u'300,00', u'300,00', u'', u'', u'', u'', u'',
                      u'', u'', u'', u'', u'', u''],
        u'documento': [u'2011NE000282', u'2011NE001531', u'2011NE001407',
                       u'2011OB805306', u'2011OB805871', u'2011OB804721',
                       u'2011OB805870', u'2011OB805307', u'2011OB804722',
                       u'2011OB808709', u'2011NE001779', u'2011NS007775',
                       u'2011NS005181', u'2011NS005182', u'2011NS004651',
                       u'2011NS004652', u'2011NS004653', u'2011NS004654',
                       u'2011NS004655', u'2011NS004656', u'2011NS003940',
                       u'2011NS003941']},
                u'geral_data': {u'num_doc': u'153037152222011NE000224',
                                u'url': u'http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222011NE000224&pagina=1',
                                u'session': u'despesasdiarias',
                                u'url_base': u'http://portaltransparencia.gov.br',
                                u'type_doc': u'empenho'}, u'dados_detalhados': {
            u'modalidade_de_licitacao': [u'NAO SE APLICA'],
            u'detalhamento_do_gasto': {u'valor_unitario_rs': [u'1,00'],
                                       u'quantidade': [1.0],
                                       u'subitem_da_despesa': [
                                           u'7 - ESTAGIARIOS'], u'descricao': [
                    u'339036-07 BOLSA MONITORIA - ARAPIRACA CI-31-2011- CPO-PROGINST.'],
                                       u'valor_total_rs': [u'1,00']},
            u'unidade_orcamentaria': [
                u'26231 - UNIVERSIDADE FEDERAL DE ALAGOAS'],
            u'esfera': [u'1 - OR\xc7AMENTO FISCAL'],
            u'modalidade_de_aplicacao': [
                u'90 - Aplic. Diretas\t(Gastos Diretos do Governo Federal)'],
            u'processo_no': [u'CI-031-2011-CPO'], u'amparo': [u''],
            u'no_convenio_contrato_de_repasse_termo_de_parceria_outros': [u''],
            u'grupo_de_despesa': [u'3 - Outras Despesas Correntes'],
            u'categoria_de_despesa': [u'3 - Despesas Correntes'],
            u'fonte_de_recursos': [
                u'12 - RECURSOS DEST.A MANUT.E DES.DO ENSINO'],
            u'elemento_de_despesa': [
                u'36 - Outros Servi\xe7os de Terceiros - Pessoa F\xedsica'],
            u'inciso': [u''],
            u'funcional_programatica': {u'autor_da_emenda': [u''], u'acao': [
                u'8282 - Reestrutura\xe7\xe3o e Expans\xe3o das Universidades Federais - REUNI'],
                                        u'funcao': [u'12 - EDUCACAO'],
                                        u'plano_orcamentario_-_po': [u'-'],
                                        u'programa': [
                                            u'1073 - BRASIL UNIVERSIT\xc1RIO'],
                                        u'linguagem_cidada': [u''],
                                        u'subtitulo_localizador': [
                                            u'0027 - No Estado de Alagoas'],
                                        u'subfuncao': [
                                            u'364 - ENSINO SUPERIOR']},
            u'tipo_de_credito': [u'A - INICIAL (LOA)'],
            u'observacao_do_documento': [u'BOLSA MONITORIA - ARAPIRACA'],
            u'referencia_da_dispensa_ou_inexigibilidade': [u''],
            u'grupo_da_fonte_de_recursos': [u'-']}}

    page_1 = open(BASE_DIR + '/page1.html').read()
    provider_html_page1 = mock.Mock()
    provider_html_page1.text = page_1.decode(encoding='utf-8')
    html1 = clean_result(provider_html_page1)

    data = {
        u'geral_data': {
            u'num_doc': u'153037152222011NE000224',
            u'session': u'despesasdiarias',
            u'type_doc': u'empenho',
            u'url': u'http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222011NE000224&pagina=1',
            u'url_base': u'http://portaltransparencia.gov.br'}
    }
    visited_links = [
        u'http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222011NE000224&pagina=1#paginacao']
    loaded_data = load_content(html1, data=data, visited_links=visited_links)

    assert loaded_data == expected
