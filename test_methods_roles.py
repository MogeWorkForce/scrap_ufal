# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from .roles import order_by_date


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
