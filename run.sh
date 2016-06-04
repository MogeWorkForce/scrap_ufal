#!/usr/bin/env bash
python main.py -u "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115" -b 30 -i > scrap.log 2>&1&

gunicorn -w 3 -b 0.0.0.0:8080 entry_point:app
