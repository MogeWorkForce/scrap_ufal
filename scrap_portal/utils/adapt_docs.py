# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from ..data_model.dao.mongodb import DocumentsDao, remove_list

MODE = os.environ.get('MODE')
if MODE == 'PROD':
    docs_dao = DocumentsDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    docs_dao = DocumentsDao(host='172.17.0.1')


def fix_old_docs_to_new_pattern():
    i = 0
    for doc in docs_dao.documents.find({}):
        key = {"_id": doc['_id']}
        # new_doc = remove_list(doc)
        new_doc = doc
        new_doc['_id'] = doc['geral_data']['num_doc']
        # docs_dao.documents.replace_one(key, new_doc, upsert=True)
        try:
            docs_dao.documents.insert(new_doc)
            docs_dao.documents.remove(key)
        except Exception as e:
            print e
        print '-' * 30, '\n', i, ' - ', key
        i += 1


if __name__ == '__main__':
    fix_old_docs_to_new_pattern()
