# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
from datetime import datetime
from scrap_portal.data_model.dao.mongodb import UrlManagerDao

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'PROD':
    url_dao = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    url_dao = UrlManagerDao(host='172.17.0.1')


def feed_urls():
    month = 75
    start_date = datetime(2010, 5, 1)

    params = [
    #     {
    #     "fase": "PAG",
    #     "codigoOS": 26000,
    #     "codigoOrgao": 26262, #SP
    #     "codigoUG": "TOD",
    #     "codigoED": 51,
    #     "codigoFavorecido": None,
    #     "consulta": "avancada"
    # },
    # {
    #     "fase": "PAG",
    #     "codigoOS": 26000,
    #     "codigoOrgao": 26241, #PARANA
    #     "codigoUG": "TOD",
    #     "codigoED": 51,
    #     "codigoFavorecido": None,
    #     "consulta": "avancada"
    # },
    # {
    #     "fase": "PAG",
    #     "codigoOS": 26000,
    #     "codigoOrgao": 26271,  #BRASILIA
    #     "codigoUG": "TOD",
    #     "codigoED": 51,
    #     "codigoFavorecido": None,
    #     "consulta": "avancada"
    # },
    # {
    #     "fase": "PAG",
    #     "codigoOS": 26000,
    #     "codigoOrgao": 26270, #Amazonas
    #     "codigoUG": "TOD",
    #     "codigoED": 51,
    #     "codigoFavorecido": None,
    #     "consulta": "avancada"
    # }
    ]

    for pr in params:
        url_dao.add_period_to_recover_in_portal(start_date, month, pr)

if __name__ == '__main__':
    feed_urls()
