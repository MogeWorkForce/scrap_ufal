# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ..data_model.dao.mongodb import DocumentsDao

import pytest


def test_remove_list():
    data = {
        "_id": 'Xpto',
        'documentos_relacionados': [
            {"a": "a", "b": "b"},
            {"a": "a", "b": "b"},
        ],
        "dados_basicos": {
            "fase": ['empenho'],
            "valor": [189],
        },
        "dados_detalhados": {
            "funcional_programatica": {
                "test": ["test"],
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
            {"a": "a", "b": "b"},
        ],
        "dados_basicos": {
            "fase": 'empenho',
            "valor": 189,
        },
        "dados_detalhados": {
            "funcional_programatica": {
                "test": "test",
                "test3": ["test", 'test2'],
                "test2": {
                    "sub_test2": "sub_test"
                }
            },
            "sub_list": "sub_list"
        }
    }

    doc = DocumentsDao()
    new_data = doc.remove_list(data)
    assert new_data == expected_data
