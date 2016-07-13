# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ..data_model.dao.mongodb import DocumentsDao
from ..utils import remove_list


def test_remove_list():
    data = {
        "_id": 'Xpto',
        'documentos_relacionados': [
            {"a": "a", "b": "b"},
        ],
        "dados_basicos": {
            "fase": ['empenho'],
            "valor": [189],
        },
        "dados_detalhados": {
            "funcional_programatica": {
                "test": [""],
                "test3": ["test", 'test2'],
                "test2": {
                    "sub_test2": ["sub_test"]
                }
            },
            "sub_list": ["sub_list"]
        }
    }

    expected_data = {
        "_id": 'Xpto',
        'documentos_relacionados': [
            {"a": "a", "b": "b"},
        ],
        "dados_basicos": {
            "fase": 'empenho',
            "valor": 189,
        },
        "dados_detalhados": {
            "funcional_programatica": {
                "test": "",
                "test3": ["test", 'test2'],
                "test2": {
                    "sub_test2": "sub_test"
                }
            },
            "sub_list": "sub_list"
        }
    }

    new_data = remove_list(data)
    assert new_data == expected_data


def test_consistence_data_in_remove_list():
    import random

    aleatory = random.randint(1, 10000)
    doc = DocumentsDao()
    dc1 = doc.documents.find({}).skip(aleatory).limit(1)[0]

    assert dc1 == remove_list(dc1)
