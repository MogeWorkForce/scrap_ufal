#!/usr/bin/env bash

gunicorn -w 2 -b 0.0.0.0:8080 hbem.api.entry_point:app &
python -m hbem.roles.analysis
if [ "$MIGRATE_DOCUMENTS" = true ]; then
    echo "Starting adapt documents!"
    python -m hbem.utils.adapt_docs
fi

#python -m hbem.main -u "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=153037152222015NE800115" -b $BATCH_URLS -i
