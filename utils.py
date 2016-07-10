# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from unicodedata import normalize


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
