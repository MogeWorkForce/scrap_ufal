# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import os
import time
from unittest import mock

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
provider_html_page2.text = page_2

# requests.get = mock.MagicMock(return_value=provider_html_page2)
time.sleep = mock.MagicMock(return_value="")


def test_parse_data():
    expected = {
        "dados_basicos": {
            "no_do_documento": "2014NE808480",
            "data": '03/12/2014',
            "descricao": "Nota de Empenho (NE)",
            "fase": "Empenho",
            "especie_tipo_de_documento": "ORIGINAL",
            "valor_do_documento": 0.0,
            "observacao_do_documento": "OBRAS EM ANDAMENTO - CONTRATO:39/13 - VIG.19/02/15 PROC.201880/14-75 - PCU PROC ORIGEM: 2012CC00017"
        },
        "dados_do_favorecido": {
            "cpf_cnpj_outros": "07.382.337/0001-50",
            "nome": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP"
        },
        "dados_do_orgao_emitente": {
            "orgao_superior": "26000 MINISTERIO DA EDUCACAO",
            "orgao_entidade_vinculada": "26241 UNIVERSIDADE FEDERAL DO PARANA",
            "unidade_gestora": "153079 UNIVERSIDADE FEDERAL DO PARANA",
            "gestao": "15232 UNIVERSIDADE FEDERAL DO PARANA"
        },
        "dados_detalhados_do_empenho": {
            "processo": "33096/2012-66",
            "esfera": "1 - Orçamento Fiscal",
            "tipo_de_credito": "A - INICIAL (LOA)",
            "fonte_de_recursos": "12 - RECURSOS DEST.A MANUT.E DES.DO ENSINO",
            "grupo_da_fonte_de_recursos": "3 - Recursos do Tesouro - Exercícios Anteriores",
            "unidade_orcamentaria": "26241 - UNIVERSIDADE FEDERAL DO PARANA",
            "area_de_atuacao_funcao": "12 - EDUCACAO",
            "subfuncao": "364 - ENSINO SUPERIOR",
            "programa": "2032 - EDUCACAO SUPERIOR - GRADUACAO, POS-GRADUACAO, ENSINO, PESQUI",
            "acao": "20RK - FUNCIONAMENTO DE INSTITUICOES FEDERAIS DE ENSINO SUPERIOR",
            "linguagem_cidada": "",
            "subtitulo_localizador": "20RK0041 - FUNCIONAMENTO DE INSTITUICOES FEDERAI - NO ESTADO DO PARANA",
            "plano_orcamentario_po": "0000 - FUNCIONAMENTO DE INSTITUICOES FEDERAIS DE ENSINO SUPERIOR",
            "regionalizacao_do_gasto": "0041 - NO ESTADO DO PARANÁ",
            "emenda_parlamentar": "@",
            "autor": "Informação do autor não disponível",
            "modalidade_da_licitacao": "Concorrência",
            "inciso": "",
            "amparo": "",
            "referencia_da_dispensa_ou_inexigibilidade": "",
            "no_convenio_outro_acordo": "",
            "categoria_da_despesa": "4 - DESPESA DE CAPITAL",
            "grupo_de_despesa": "4 - INVESTIMENTOS",
            "modalidade_de_aplicacao": "90 - APLICACOES DIRETAS",
            "elemento_de_despesa": "51 - OBRAS E INSTALACOES",
        },
        "detalhamento_do_gasto": [{
            "subitem": "91 - OBRAS EM ANDAMENTO",
            "quantidade": 1,
            "valor_unitario_rs": 166200.0,
            "valor_total_rs": 166200.0,
            "descricao": "SERVICO ENGENHARIA 000022225 Obra de Construção do Edifício do Depósito de Móveis Novos e Reforma do Barracão de Inservíveis para adequação ao Depósito do Restaurante Universitário, Campus Centro Politécnico, desta UFPR."
        }],
        "documentos_relacionados": [
            {
                "data": "12/01/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB800254",
                "documentoResumido": "2015OB800254",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "98.785,75"
            },
            {
                "data": "19/05/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB804077",
                "documentoResumido": "2015OB804077",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "49.173,36"
            },
            {
                "data": "12/01/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DF800461",
                "documentoResumido": "2015DF800461",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "6.271,25"
            },
            {
                "data": "19/05/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DF802068",
                "documentoResumido": "2015DF802068",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "3.121,67"
            },
            {
                "data": "12/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322014DR800417",
                "documentoResumido": "2014DR800417",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "2.144,02"
            },
            {
                "data": "17/04/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DR800102",
                "documentoResumido": "2015DR800102",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "1.201,69"
            },
            {
                "data": "06/07/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB806578",
                "documentoResumido": "2015OB806578",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "61.683,32"
            },
            {
                "data": "03/06/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322015NS013241",
                "documentoResumido": "2015NS013241",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            },
            {
                "data": "16/04/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322015NS007115",
                "documentoResumido": "2015NS007115",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            },
            {
                "data": "31/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322014NS028776",
                "documentoResumido": "2014NS028776",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "Sem informação",
                "valor": ""
            },
            {
                "data": "10/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322014NS027217",
                "documentoResumido": "2014NS027217",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            }
        ]
    }

    html = open(BASE_DIR + '/base.html').read()
    provider_html = mock.Mock()
    provider_html.text = html
    html = clean_result(provider_html)

    data = {
        u'geral_data': {
            u'num_doc': u'153079152322014NE808480',
            u'session': u'despesas',
            u'type_doc': u'empenho',
            u'url': u'http://portaltransparencia.gov.br/despesas/empenho/153079152322014NE808480?ordenarPor=fase&direcao=desc',
            u'url_base': u'http://portaltransparencia.gov.br'},
        "detalhamento_do_gasto": [{
            "subitem": "91 - OBRAS EM ANDAMENTO",
            "quantidade": 1,
            "valor_unitario_rs": 166200,
            "valor_total_rs": 166200,
            "descricao": "SERVICO ENGENHARIA 000022225 Obra de Construção do Edifício do Depósito de Móveis Novos e Reforma do Barracão de Inservíveis para adequação ao Depósito do Restaurante Universitário, Campus Centro Politécnico, desta UFPR."
        }],
        "documentos_relacionados": [
            {
                "data": "12/01/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB800254",
                "documentoResumido": "2015OB800254",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "98.785,75"
            },
            {
                "data": "19/05/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB804077",
                "documentoResumido": "2015OB804077",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "49.173,36"
            },
            {
                "data": "12/01/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DF800461",
                "documentoResumido": "2015DF800461",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "6.271,25"
            },
            {
                "data": "19/05/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DF802068",
                "documentoResumido": "2015DF802068",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "3.121,67"
            },
            {
                "data": "12/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322014DR800417",
                "documentoResumido": "2014DR800417",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "2.144,02"
            },
            {
                "data": "17/04/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015DR800102",
                "documentoResumido": "2015DR800102",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "1.201,69"
            },
            {
                "data": "06/07/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Pagamento",
                "documento": "153079152322015OB806578",
                "documentoResumido": "2015OB806578",
                "especie": "Original",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": "61.683,32"
            },
            {
                "data": "03/06/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322015NS013241",
                "documentoResumido": "2015NS013241",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            },
            {
                "data": "16/04/2015",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322015NS007115",
                "documentoResumido": "2015NS007115",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            },
            {
                "data": "31/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322014NS028776",
                "documentoResumido": "2014NS028776",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "Múltiplo",
                "favorecido": "Sem informação",
                "valor": ""
            },
            {
                "data": "10/12/2014",
                "flgExisteDocumentoRelacionadoNoDM": True,
                "fase": "Liquidação",
                "documento": "153079152322014NS027217",
                "documentoResumido": "2014NS027217",
                "especie": "",
                "orgaoSuperior": "MINISTERIO DA EDUCACAO",
                "orgaoVinculado": "UNIVERSIDADE FEDERAL DO PARANA",
                "unidadeGestora": "UNIVERSIDADE FEDERAL DO PARANA",
                "elementoDespesa": "OBRAS E INSTALACOES",
                "favorecido": "KUMER ENGENHARIA E CONSTRUCOES - EIRELI - EPP",
                "valor": ""
            }
        ]
    }
    loaded_data = load_content(html, data=data)
    loaded_data.pop("documentos_relacionados")
    loaded_data.pop("detalhamento_do_gasto")
    loaded_data.pop("geral_data")
    expected.pop("documentos_relacionados")
    expected.pop("detalhamento_do_gasto")
    # print(json.dumps(loaded_data, indent=2))
    assert loaded_data == expected
