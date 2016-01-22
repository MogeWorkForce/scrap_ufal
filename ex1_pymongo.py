# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


client = MongoClient()
db = client.test

collect = db.documents

def using_replace_one(client):
	for i in range(100):
		try:
			value = "2015011231"
			if i > 0:
				value = value+str(i)
				key = {"_id": value}
			else:
				key = {"_id": value}

			result = collect.replace_one(
				key,{
					"_id": value,
					"dados_relacionados": {
						"fase": "Empenho",
						"tipo_documento": "Sei la"
					}
				},
				upsert=True
			)
		except DuplicateKeyError as e:
			print e

def using_update_one(cient):
	for i in range(100):
		try:
			value = "2015011231"
			if i > 0:
				value = value+str(i)
				key = {"_id": value}
			else:
				key = {"_id": value}

			result = collect.update_one(
				key,{"$set":{
						"_id": value,
						"dados_relacionados": {
							"fase": "Empenho",
							"tipo_documento": "Sei la"
						}
					}
				},
				upsert=True
			)
		except DuplicateKeyError as e:
			print e

if __name__ == '__main__':
	using_update_one()
	using_replace_one()