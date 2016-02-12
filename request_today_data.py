# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
from datetime import date, timedelta
import argparse
import logging
import re

link_match = re.compile(r'a href="(?P<link_url>[^"]*)"?')
match = re.compile(r'<table class="tabela">(.*?)<\/table>')

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

log_proactive = logging.getLogger("Scrap_Ufal.pro_active")
log_proactive.setLevel(level_debug)

'''
periodoInicio
periodoFim
fase
codigoOS
codigoOrgao
codigoUG
codigoED
codigoFavorecido
consulta
'''


fmt_data = "%d/%m/%Y"

def clean_result(result):
    return result.text.replace('\n', '').replace('  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')


def main(date_start=None, before=False, time_elapse=1):
    url_base = "http://portaltransparencia.gov.br/despesasdiarias/"
    url = url_base+"resultado"

    #elapse = timedelta(days=time_elapse)
    elapse = timedelta(days=15)

    if not date_start:
        date_start = date.today()

    datas = [date_start.strftime(fmt_data), (
            date_start-elapse if not before else date_start+elapse
        ).strftime(fmt_data)
    ]

    datas.sort()

    params = {
        "periodoInicio": datas[1],
        "periodoFim": datas[0],
        "fase": "PAG",
        "codigoOS": 26000,
        "codigoOrgao": 26231,
        "codigoUG": "TOD",
        "codigoED": "TOD",
        "codigoFavorecido": None,
        "consulta": "avancada"
    }

    result = requests.get(url, params=params)
    all_links = []
    tables = match.findall(clean_result(result))
    print '-------------------', len(tables)
    for content in tables:
        links = link_match.findall(content)
        all_links.extend(links)

    all_links = [url_base+item for item in all_links]
    print all_links
    print result.url

if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(
        description="Set a Url to crawler the new notas_empenho inserted on evaluated period"
    )

    parser.add_argument("-u", "--url", type=str,
                        help="Url to search notas_empenhos")
        """
    main()
