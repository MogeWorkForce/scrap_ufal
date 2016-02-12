# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from apscheduler.schedulers.background import BackgroundScheduler
from scrap_request import load_url_from_queue, get_content_page
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import time
import logging
import sys
import traceback
import argparse

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


if __name__ == '__main__':
    executors = {
        'default': ThreadPoolExecutor(10),
        'processpool': ProcessPoolExecutor(5),
    }

    job_defaults = {
        'coalesce': False,
        'max_instances': 2
    }

    logScheduller = logging.getLogger('Scrap_Ufal.Multiprocess')
    logScheduller.setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler(
        logger=logScheduller, executors=executors, job_defaults=job_defaults)
    # scheduler._logger.setLevel(logging.WARNING)
    parser = argparse.ArgumentParser(description="Set a Url to crawler")
    parser.add_argument('-u', '--url', type=str,
                        help="Url to search notas_empenhos")

    parser.add_argument('-b', '--batch', type=int, choices=range(1, 21),
                        help="How many urls will be loaded inside the queue")

    parser.add_argument('-i', '--ignore', action="store_true",
                        help="Ignore url passed")

    args = parser.parse_args()
    if not args.ignore:
        if not args.url:
            raise Exception("Url not passed, please set a url in arguments")
    else:
        logger.warning("Start ignoring url passed on parameter")

    url = args.url
    batch = args.batch

    url_on_queue = lambda: load_url_from_queue(int(batch))
    url_on_fallback = lambda: load_url_from_queue(
        int(batch) if int(batch) <= 2 else int(round(int(batch)/2.0)),
        collection="fallback"
    )

    try:
        if not args.ignore:
            visited_links = [url]
            get_content_page(url, visited_links=visited_links)
        # url_on_queue()
    except Exception as e:
        traceback.print_exc()
        logger.debug("Error on load content on url passed")
        # sys.exit(1)

    scheduler.add_job(url_on_queue, trigger='interval', seconds=15)
    #scheduler.add_job(url_on_queue, trigger='interval', seconds=36)
    scheduler.add_job(url_on_fallback, trigger='interval', seconds=22)
    scheduler.start()

    try:
        while True:
            time.sleep(30)

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
