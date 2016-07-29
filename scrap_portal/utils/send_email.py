# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import smtplib

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

EMAIL = os.environ.get('EMAIL', 'exemogenes@gmail.com')


def send_email(recipients, message, subject, file_name=None, file_to_body=None):
    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]
    emaillist = [elem.strip().split(',') for elem in recipients]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['Reply-to'] = EMAIL

    msg.preamble = message

    part = MIMEText("teste aqui.")

    if file_to_body:
        with open(file_to_body, "rb") as file_opened:
            part = MIMEText(file_opened.read())

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