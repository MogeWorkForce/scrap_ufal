#!/usr/bin/env bash
gunicorn -w 2 -b 0.0.0.0:8080 entry_point:app > scrap.log 2>&1&

python main.py -u "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115" -b 20 -i -j 2
