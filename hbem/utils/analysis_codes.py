# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

NULL_VALUE_EMPENHADO = 11
BIDDING_NOT_FOUND = 12
WRONG_BIDDING = 21
EXCEDED_LIMIT_OF_PAYMENTS = 22

part_null_empenho = "Nota de Empenho com valor 0 após checkar o "
part_null_empenho += "limite de pagamento da Nota de Empenho."


VERBOSE_ERROR_TYPE = {
    NULL_VALUE_EMPENHADO: part_null_empenho,
    BIDDING_NOT_FOUND: "Modalide de Licitação não Encontrada.",
    WRONG_BIDDING: "Modalide de Licitação Errada",
    EXCEDED_LIMIT_OF_PAYMENTS: "Excedeu o limite de pagamento",
}
