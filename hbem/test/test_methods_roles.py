# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ..roles.analysis import order_by_date, retrieve_payment_by_empenho


def test_check_extrapolar_amount():
    data = [
        {u'data': u'2015-06-18 00:00:00.0',
         u'documento': u'2015NS005911',
         u'valor_rs': 0.0},
        {u'data': u'2015-12-31 00:00:00.0',
         u'documento': u'2015NS011510',
         u'valor_rs': 0.0},
        {u'data': u'2016-11-31 00:00:00.0',
         u'documento': u'2016NS001382',
         u'valor_rs': 0.0},
        {u'data': u'2016-05-20 00:00:00.0',
         u'documento': u'2016DF800526',
         u'valor_rs': 1715.43},
        {u'data': u'2016-05-19 00:00:00.0',
         u'documento': u'2016DR800443',
         u'valor_rs': 733.09},
        {u'data': u'2016-05-20 00:00:00.0',
         u'documento': u'2016OB803449',
         u'valor_rs': 26875.1}
    ]

    expected = [
        {u'data': u'2015-06-18 00:00:00.0',
         u'documento': u'2015NS005911',
         u'valor_rs': 0.0},
        {u'data': u'2015-12-31 00:00:00.0',
         u'documento': u'2015NS011510',
         u'valor_rs': 0.0},
        {u'data': u'2016-05-19 00:00:00.0',
         u'documento': u'2016DR800443',
         u'valor_rs': 733.09},
        {u'data': u'2016-05-20 00:00:00.0',
         u'documento': u'2016DF800526',
         u'valor_rs': 1715.43},
        {u'data': u'2016-05-20 00:00:00.0',
         u'documento': u'2016OB803449',
         u'valor_rs': 26875.1},
        {u'data': u'2016-11-31 00:00:00.0',
         u'documento': u'2016NS001382',
         u'valor_rs': 0.0},
    ]

    assert expected == order_by_date(data)


def test_retrieve_payment_to_this_empenho():
    doc_empenho_id = "2015NE800391"
    nota_pagamento = {u'dados_detalhados': {
        u'modalidade_de_aplicacao': u'90 - Aplic. Diretas(Gastos Diretos do Governo Federal)',
        u'processo_no': u'23065.019628/2015-14',
        u'grupo_de_despesa': u'4- Investimentos',
        u'categoria_de_despesa': u'4- Despesas de Capital',
        u'elemento_de_despesa': u'51 - OBRAS E INSTALACOES',
        u'observacao_do_documento': u'PAGAMENTO DA NFS 1001991, REF. A16 MEDI\xc7\xc3O DA CONSTRU\xc7\xc3O DA SUBESTA\xc7\xc3O DE 69KVA, E LINHA DE TRANSMISS\xc3O DO CAMPUS A. C. SIM\xd5ES EM MACEIO. CONTRATO 28/2013 PROCESSO.23065.019628/2015-14.',
        u'detalhamento_do_documento': {u'valor_rs': 146292.12,
                                       u'cancelamento_estorno': u'N\xe3o',
                                       u'empenho': u'2015NE800391',
                                       u'subitem_da_despesa': u'91 - OBRAS EM ANDAMENTO',
                                       u'convenio_outros': [0.0]}},
        u'documentos_relacionados': [
            {u'favorecido': u'PRENER-COMERCIO DE MATERIAIS ELETRICOS LTDA',
             u'especie': u'Original',
             u'unidade_gestora': u'UNIVERSIDADE FEDERAL DE ALAGOAS',
             u'elemento_de_despesa': u'OBRAS E INSTALACOES',
             u'orgao_entidade_vinculada': u'UNIVERSIDADE FEDERAL DE ALAGOAS',
             u'orgao_superior': u'MINISTERIO DA EDUCACAO',
             u'fase': u'Empenho', u'data': u'2015-04-30 00:00:00.0',
             u'valor_rs': 710969.31, u'documento': u'2015NE800391'}],
        u'dados_basicos': {
            u'favorecido': u'00.930.087/0001-04- PRENER-COMERCIO DE MATERIAIS ELETRICOS LTDA',
            u'tipo_de_ob': u'OBC PARA TERCEIROS NO MESMO BANCO',
            u'valor': 146292.12,
            u'tipo_de_documento': u'Ordem Banc\xe1ria (OB)',
            u'gestao': u'15222 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'unidade_gestora_emitente': u'153037 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'orgao_entidade_vinculada': u'26231 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'orgao_superior': u'26000 - MINISTERIO DA EDUCACAO',
            u'fase': u'Pagamento', u'data': u'2016-01-18 00:00:00.0',
            u'documento': u'2016OB800667'}, u'date_saved': 20160713,
        u'_id': u'2016OB800667'}

    nota_pagamento2 = {u'dados_detalhados': {
        u'modalidade_de_aplicacao': u'90 - Aplic. Diretas(Gastos Diretos do Governo Federal)',
        u'processo_no': u'23065.019628/2015-14',
        u'grupo_de_despesa': u'4- Investimentos',
        u'categoria_de_despesa': u'4- Despesas de Capital',
        u'elemento_de_despesa': u'51 - OBRAS E INSTALACOES',
        u'observacao_do_documento': u'PAGAMENTO DA NFS 1001991, REF. A16 MEDI\xc7\xc3O DA CONSTRU\xc7\xc3O DA SUBESTA\xc7\xc3O DE 69KVA, E LINHA DE TRANSMISS\xc3O DO CAMPUS A. C. SIM\xd5ES EM MACEIO. CONTRATO 28/2013 PROCESSO.23065.019628/2015-14.',
        u'detalhamento_do_documento': {u'valor_rs': [146292.12],
                                       u'cancelamento_estorno': [u'N\xe3o'],
                                       u'empenho': [u'2015NE800391'],
                                       u'subitem_da_despesa': [u'91 - OBRAS EM ANDAMENTO'],
                                       u'convenio_outros': [0.0]}},
        u'documentos_relacionados': [
            {u'favorecido': u'PRENER-COMERCIO DE MATERIAIS ELETRICOS LTDA',
             u'especie': u'Original',
             u'unidade_gestora': u'UNIVERSIDADE FEDERAL DE ALAGOAS',
             u'elemento_de_despesa': u'OBRAS E INSTALACOES',
             u'orgao_entidade_vinculada': u'UNIVERSIDADE FEDERAL DE ALAGOAS',
             u'orgao_superior': u'MINISTERIO DA EDUCACAO',
             u'fase': u'Empenho', u'data': u'2015-04-30 00:00:00.0',
             u'valor_rs': 710969.31, u'documento': u'2015NE800391'}],
        u'dados_basicos': {
            u'favorecido': u'00.930.087/0001-04- PRENER-COMERCIO DE MATERIAIS ELETRICOS LTDA',
            u'tipo_de_ob': u'OBC PARA TERCEIROS NO MESMO BANCO',
            u'valor': 146292.12,
            u'tipo_de_documento': u'Ordem Banc\xe1ria (OB)',
            u'gestao': u'15222 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'unidade_gestora_emitente': u'153037 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'orgao_entidade_vinculada': u'26231 - UNIVERSIDADE FEDERAL DE ALAGOAS',
            u'orgao_superior': u'26000 - MINISTERIO DA EDUCACAO',
            u'fase': u'Pagamento', u'data': u'2016-01-18 00:00:00.0',
            u'documento': u'2016OB800667'}, u'date_saved': 20160713,
        u'_id': u'2016OB800667'}

    expected = 146292.12
    zero_expected = 0
    dummy_doc_empenho_id = 'XPTO'
    retrieved = retrieve_payment_by_empenho(nota_pagamento, doc_empenho_id)
    retrieved2 = retrieve_payment_by_empenho(nota_pagamento2, doc_empenho_id)
    retrieved3 = retrieve_payment_by_empenho(
        nota_pagamento2, dummy_doc_empenho_id)
    assert expected == retrieved
    assert expected == retrieved2
    assert zero_expected == retrieved3
