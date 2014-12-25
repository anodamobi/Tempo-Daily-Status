#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'themengzor'

import requests
import ConfigParser
from datetime import date
from xml.etree import ElementTree
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sys

# fixing pwd
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

today = date.today()

configFile = ConfigParser.ConfigParser()

def tree2dict(element):
    result = {}
    for child in element._children:
        if len(child._children) > 0:
            result[child.tag] = tree2dict(child)
        else:
            result[child.tag] = child.text
    return result

try:
    configFile.read('tds.conf')
except:
    print 'Unable to read config file ./tds.conf'
    exit(1)

globalConfig = {}
smtpConfig = {}
tempoConfig = {}

# reading config
try:
    globalConfig['emails'] = [x.strip() for x in configFile.get('global', 'emails').split(',')]
    smtpConfig['server'] = configFile.get('smtp', 'server')
    smtpConfig['port'] = configFile.get('smtp', 'port')
    smtpConfig['security'] = configFile.get('smtp', 'security')
    smtpConfig['auth'] = configFile.get('smtp', 'auth')
    smtpConfig['login'] = configFile.get('smtp', 'login')
    smtpConfig['password'] = configFile.get('smtp', 'password')
    smtpConfig['from'] = configFile.get('smtp', 'from')
    tempoConfig['baseurl'] = configFile.get('tempo', 'baseurl')
    tempoConfig['token'] = configFile.get('tempo', 'token')
except Exception as e:
    print 'Unable to parse config file'
    print e.message
    exit(1)

# getting worklogs
worklogs = []
try:
    url = tempoConfig['baseurl']
    url += '/plugins/servlet/tempo-getWorklog/'
    url += '?dateFrom=%s-%s-%s' % (today.year, today.month, today.day)
    url += '&dateTo=%s-%s-%s' % (today.year, today.month, today.day)
    url += '&format=xml'
    url += '&diffOnly=false'
    url += '&addUserDetails=true'
    url += '&addApprovalStatus=true'
    url += '&addBillingInfo=true'
    url += '&addIssueDescription=true'
    url += '&addIssueDetails=true'
    url += '&addIssueSummary=true'
    url += '&addWorklogDetails=true'
    url += '&tempoApiToken=%s' % tempoConfig['token']
    request = requests.get(url)
except Exception as e:
    print 'Unable to get worklogs due the error:'
    print e.message
    exit(1)
else:
    tree = ElementTree.fromstring(request.content)
    worklogKeys = []
    for worklog in tree:
        item = tree2dict(worklog)
        worklogs.append(item)

users = {}
for worklog in worklogs:
    if not users.has_key(worklog['username']):
        users[worklog['username']] = {
            'worklogs': [],
            'stats': {
                'total_hours': 0.0,
                'total_worklogs': 0,
                'workload': 0
            },
            'full_name': worklog['user_details']['full_name']
        }
    users[worklog['username']]['worklogs'].append(worklog)
    users[worklog['username']]['stats']['total_hours'] += float(worklog['hours'])
    users[worklog['username']]['stats']['total_worklogs'] += 1
    users[worklog['username']]['stats']['workload'] = min(8, users[worklog['username']]['stats']['total_hours']) / 8 * 100

data = {
    'date': today
}

template = Template(open('templates/daily-report.html').read())
result = template.render(users=users, globalConfig=globalConfig, tempoConfig=tempoConfig, data=data)

# preparing message
msg = MIMEMultipart('alternative')
msg['Subject'] = "Your team TEMPO worklogs"
msg['From'] = 'Tempo Daily Status <%s>' % smtpConfig['from']
msg['To'] = ", ".join(globalConfig['emails'])

msg.attach(MIMEText('This is HTML email', 'plain'))
msg.attach(MIMEText(result.encode('UTF-8'), 'html'))

# sending email
if smtpConfig['security'] == 'ssl':
    mail = smtplib.SMTP_SSL()
else:
    mail = smtplib.SMTP()

# mail.set_debuglevel(1)

try:
    mail.connect(smtpConfig['server'], smtpConfig['port'])
    mail.login(smtpConfig['login'], smtpConfig['password'])
    mail.sendmail(msg['From'], globalConfig['emails'], msg.as_string())
    mail.quit()
except Exception as e:
    print 'Unable to send email:'
    print e.message
    exit(1)
else:
    print 'Email sent to', globalConfig['emails']

# EOF
