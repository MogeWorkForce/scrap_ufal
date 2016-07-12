# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

NULL_VALUE_EMPENHADO = 11
BIDDING_NOT_FOUND = 12
WRONG_BIDDING = 21
EXCEDED_LIMIT_OF_PAYMENTS = 22

VERBOSE_ERROR_TYPE = {
    NULL_VALUE_EMPENHADO: "'Nota de Empenho' with 0 value after check limit.",
    BIDDING_NOT_FOUND: "Bidding mode not found",
    WRONG_BIDDING: "Wrong bidding mode",
    EXCEDED_LIMIT_OF_PAYMENTS: "Exceded limit of payments",
}