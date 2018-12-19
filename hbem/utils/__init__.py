# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import re
from unicodedata import normalize

match_span = re.compile(r'<span class="aviso_lista">.*?</span>?')
REMOVE_TRASH_REGEX = re.compile(r"[_/]{1,}")
REMOVE_SPACES_REGEX = re.compile(r"\s{1,}")

formatter = logging.Formatter(
    "[%(name)s][%(levelname)s][PID %(process)d][%(asctime)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("HBEM")
level_debug = logging.INFO
logger.setLevel(level_debug)
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

NOT_ALLOWED_CLEAN = ('documentos_relacionados',)


def clean_result(result):
    txt = result.text.replace("\t", " ").\
        replace('\n', '').\
        replace('&nbsp;', ' ')
    txt = match_span.sub('', txt)
    return txt


def normalize_text(txt, codif='utf-8'):
    txt = REMOVE_TRASH_REGEX.sub(
        "_", normalize('NFKD', txt).
            replace(" ", "_").
            replace("-", "_").
            replace(':', '').
            replace("(", "").
            replace(")", "").
            replace("$", "s").
            replace("/", "_/_").
            replace('_/_', '_').
            encode("ascii", "ignore").
            decode('utf-8').
            lower())
    return txt


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
