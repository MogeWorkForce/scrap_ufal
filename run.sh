#!/usr/bin/env bash
gunicorn -w 2 -b 0.0.0.0:8080 scrap_portal.api.entry_point:app > scrap.log 2>&1&

python -m scrap_portal.main -u "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115" -b $BATCH_URLS -i
