# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import smtplib

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

EMAIL = os.environ.get('EMAIL', 'exemogenes@gmail.com')
pattern_url_accesss = "http://portaltransparencia.gov.br/despesasdiarias/empenho?documento=%s"


def send_email(recipients, message, subject, file_name=None, information_body=None):
    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]
    emaillist = [elem.strip().split(',') for elem in recipients]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['Reply-to'] = EMAIL

    msg.preamble = message

    part = MIMEText("teste aqui.")

    if information_body:
        txt = generate_report(
            information_body['total'], information_body['total_correct'],
            information_body['total_error'], information_body['payload']
        )
        part = MIMEText(txt)

        msg.attach(part)

    if file_name:
        with open(file_name, "rb") as file_opened:
            part = MIMEApplication(file_opened.read())
        file_name_sended = file_name.split('/')[-1]
        part.add_header(
            'Content-Disposition', 'attachment', filename=file_name_sended)
        msg.attach(part)
        os.remove(file_name)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.login(EMAIL, os.environ['PASSWORD'])

    server.sendmail(msg['From'], emaillist, msg.as_string())


def generate_report(total, corrects, errors, payload_erros):

    msg = "Relatorio de Conclusão de Análise"
    msg += "\n\n"
    msg += "Total Certas: %d\n" % corrects
    msg += "Total com Erros: %d\n" % errors
    msg += "Total Analisadas: %d\n\n\n" % total
    msg += "Detalhamento das Notas de Empenho com anomalias:\n\n"

    i = 1
    for key, value in payload_erros.iteritems():
        urls_access = pattern_url_accesss % key

        msg += "%d - Url: %s\n" % (i, urls_access)
        msg += "\tDocumento: %s\n" % key
        msg += "\tGestão: "
        msg += "%s\n" % value['gestao']
        msg += "\tUnidade Gestora Emitente: %s\n" % value['unidade_gestora_emitente']
        for error in value['error']:
            error_name = error['error']
            msg += "\t\t"
            msg += error_name
            msg += '\n'

        msg += '\n'
        i += 1

    return msg.encode(
            encoding='utf-8')