# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import argparse
import logging
import os
import time
import traceback
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

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

from .data_model.dao.mongodb import ProxiesDao, SystemConfigDao
from .crawlers.scrap_request import load_url_from_queue, get_content_page
from .crawlers.request_range_date import get_random_batch

MODE = os.environ.get('MODE', 'DEV')

if MODE == 'PROD':
    proxy_dao = ProxiesDao(os.environ.get('MONGODB_ADDON_URI'))
    system_configs = SystemConfigDao(os.environ.get('MONGODB_ADDON_URI'))
else:
    proxy_dao = ProxiesDao(host='172.17.0.1')
    system_configs = SystemConfigDao(host='172.17.0.1')


def manager_queue_job(function, status=True):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set a Url to crawler")
    parser.add_argument('-u', '--url', type=str,
                        help="Url to search notas_empenhos")

    parser.add_argument('-b', '--batch', type=int, choices=range(1, 31),
                        help="How many urls will be loaded inside the queue")

    parser.add_argument('-i', '--ignore', action="store_true",
                        help="Ignore url passed")

    args = parser.parse_args()
    if not args.ignore:
        if not args.url:
            raise Exception("Url not passed, please set a url in arguments")
    else:
        logger.warning("Start ignoring url passed on parameter")

    executors = {
        'default': ThreadPoolExecutor(10),
        'processpool': ProcessPoolExecutor(5),
    }

    num_jobs = os.environ.get('NUMBER_JOBS')
    job_defaults = {
        'coalesce': False,
        'max_instances': int(num_jobs) if num_jobs else 3
    }

    logScheduller = logging.getLogger('Scrap_Ufal.Multiprocess')
    logScheduller.setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler(
        logger=logScheduller, executors=executors, job_defaults=job_defaults)
    # scheduler._logger.setLevel(logging.WARNING)

    proxy_dao.release_all_proxies()
    url = args.url
    batch = args.batch

    url_on_queue = lambda: load_url_from_queue(int(batch))
    url_on_fallback = lambda: load_url_from_queue(
        int(batch) if int(batch) <= 2 else int(round(int(batch) / 2.0)),
        collection="fallback"
    )
    url_on_finder_urls_notas = lambda: get_random_batch(1)

    try:
        if not args.ignore:
            visited_links = [url]
            get_content_page(url, visited_links=visited_links)
        else:
            get_random_batch(batch_size=1)
    except Exception as e:
        traceback.print_exc()
        logger.debug("Error on load content on url passed")

    queue_job = scheduler.add_job(url_on_queue, trigger='interval', seconds=15)
    fallback_job = scheduler.add_job(
        url_on_fallback, trigger='interval', seconds=25)
    finder_urls_notas_job = scheduler.add_job(
        url_on_finder_urls_notas, trigger='interval', minutes=1, seconds=30)
    scheduler.start()

    fallback_job.modify(max_instances=1)
    finder_urls_notas_job.modify(max_instances=1)

    try:
        while True:
            time.sleep(60)
            config = system_configs.get_configs()
            system_up = config['system_up']

            queue_active = config['queue']
            fallback_active = config['fallback']
            finder_urls_notas_active = config['url_on_finder_urls_notas']
            if not system_up:
                logScheduller.warning(
                    "The Jobs will be shutdown in few moments")
                sys.exit(0)

    except (KeyboardInterrupt, SystemExit):
        proxy_dao.release_all_proxies()
        scheduler.shutdown()
