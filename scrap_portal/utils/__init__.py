# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from unicodedata import normalize

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

NOT_ALLOWED_CLEAN = ('documentos_relacionados',)


def clean_result(result):
    return result.text.replace('\n', '').replace(
        '  ', '').replace('&nbsp;', ' ').replace('&nbsp', ' ')


def normalize_text(txt, codif='utf-8'):
    if isinstance(txt, str):
        txt = txt.decode(codif, "ignore")
    return normalize('NFKD', txt).encode('ASCII', 'ignore'). \
        replace(" ", "_"). \
        replace(':', ''). \
        replace("(", ""). \
        replace(")", ""). \
        replace("$", "s").lower()


def remove_list(doc):
    tmp_doc = {}
    for key, value in doc.iteritems():
        if key in NOT_ALLOWED_CLEAN:
            tmp_doc[key] = value
            continue
        new_value = None
        if isinstance(value, (dict,)):
            new_value = remove_list(value)
        elif isinstance(value, (list, tuple, set)):
            new_value = value[0] if len(value) == 1 else value
        tmp_doc[key] = new_value if new_value is not None else value

    return tmp_doc
