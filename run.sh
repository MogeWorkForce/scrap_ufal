#!/usr/bin/env bash

gunicorn -w 2 -b 0.0.0.0:8080 scrap_portal.api.entry_point:app &

if [ "$MIGRATE_DOCUMENTS" = true ]; then
    echo "Starting adapt documents!"
    python -m scrap_portal.utils.adapt_docs
fi

python -m scrap_portal.main -u "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115" -b $BATCH_URLS -i
