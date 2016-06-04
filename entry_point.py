# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from bottle import Bottle, run, request, response
from gevent import monkey, queue; monkey.patch_all()
from data_model.dao.mongodb import UrlManagerDao
from gevent.pywsgi import WSGIServer
from datetime import date
import os
import json
import logging
import functools
import traceback

__author__ = 'hermogenes'

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

logRest = logging.getLogger("Scrap_Ufal.RESTAPI")
logRest.setLevel(logging.DEBUG)

app = Bottle()
app.patch = functools.partial(app.route, method='PATCH')

APP_NAME = "scrapufal"
VERSION = "v1"

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'DEV':
    client = UrlManagerDao()
elif MODE == "DOCKER":
    client = UrlManagerDao(host='172.17.0.1')
else:
    client = UrlManagerDao(os.environ.get('MONGODB_ADDON_URI'))

NAME_VERSION = "/%s/%s/" % (APP_NAME, VERSION)
@app.put(NAME_VERSION+"urls")
def insert_urls():
    body_error = {"message": {"errors": [], "success": False}}
    if request.headers.get('Content-Type') != "application/json":
        logRest.warning("Invalid Content-Type")
        body_error['message']['errors'].append("Invalid Content-Type")
        return body_error

    data = request.json

    try:
        list_urls = data['urls']
        client.set_chunk_url(list_urls)
    except Exception as e:
        error_msg = str(e)
        logRest.warning(error_msg)
        body_error['message']['errors'].append(error_msg)
        return body_error

    return {"message": {"success": True}}


@app.get(NAME_VERSION+"status/urls/<collection>")
def status_enqueue(collection):
    body_error = {"message": {"errors": [], "success": False}}
    if request.headers.get('Content-Type') != "application/json":
        logRest.warning("Invalid Content-Type")
        body_error['message']['errors'].append("Invalid Content-Type")
        return body_error

    key = {"_id": date.today().strftime("%Y%m%d")}
    try:
        result = client.db_urls[collection].find_one(key)
    except:
        traceback.print_exc()
        result = {"urls": []}

    return {
        "message":
        {"success": True, "result": "%s have: %s" % (collection.upper(), len(result['urls']))}
    }


def run_app():

    run(app, host='localhost', port=9000, debug=True, reloader=True, server='gevent')
    #run(app, host='localhost', port=9000, debug=True, reloader=True)
    #server = WSGIServer(('localhost', 9000), app)
    #server.serve_forever()

if __name__ == '__main__':
    run_app()
