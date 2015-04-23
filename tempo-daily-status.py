#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Alex Zavrazhniy <alex@anoda.mobi>'

import requests
import ConfigParser
import sys
import smtplib
import os
from datetime import date, datetime
from xml.etree import ElementTree
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def human_time(hours):
    if hours is None:
        return '0'

    h, m = divmod(float(hours) * 60, 60)
    if int(m) is not 0:
        return '%dh %dm' % (h, m)
    else:
        return '%dh' % h


try:
    configFile.read('tds.conf')
except:
    print 'Unable to read config file ./tds.conf'
    print 'Copy ./tds.conf.template to ./tds.conf and fill it with your credentials'
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
    params = {
        'dateFrom': '%s-%s-%s' % (today.year, today.month, today.day-1),
        'dateTo': '%s-%s-%s' % (today.year, today.month, today.day-1),
        'format': 'xml',
        'diffOnly': 'false',
        'addUserDetails': 'true',
        'addApprovalStatus': 'true',
        'addBillingInfo': 'true',
        'addIssueDescription': 'true',
        'addIssueDetails': 'true',
        'addIssueSummary': 'true',
        'addWorklogDetails': 'true',
        'tempoApiToken': tempoConfig['token']
    }
    request = requests.get(url, params=params)
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
    if worklog['username'] not in users:
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
    worklog['issue_details']['original_estimate_human'] = human_time(worklog['issue_details'].get('original_estimate', 0))
    worklog['issue_details']['remaining_estimate_human'] = human_time(worklog['issue_details'].get('remaining_estimate', 0))
    worklog['hours_human'] = human_time(worklog['hours'])
    worklog['worklog_details']['created_human'] = datetime.strptime(worklog['worklog_details']['created'], '%Y-%m-%d %H:%M:%S').strftime('%b %-d, %H:%M:%S')
    worklog['worklog_details']['updated_human'] = datetime.strptime(worklog['worklog_details']['updated'], '%Y-%m-%d %H:%M:%S').strftime('%b %-d, %H:%M:%S')

for username, user in users.iteritems():
    user['stats']['total_hours_human'] = human_time(user['stats']['total_hours'])

data = {
    'date': today
}

template = Template(open('templates/daily-report.html').read().decode('UTF-8'))
result = template.render(users=users, globalConfig=globalConfig, tempoConfig=tempoConfig, data=data).encode('UTF-8')

# Debug
# f = open('/tmp/tds.html', 'w')
# f.write(result)
# f.close()
# os.system("open /tmp/tds.html")
# exit()
# / Debug

# preparing message
msg = MIMEMultipart('alternative')
msg['Subject'] = "Your team TEMPO worklogs"
msg['From'] = 'Tempo Daily Status <%s>' % smtpConfig['from']
msg['To'] = ", ".join(globalConfig['emails'])

msg.attach(MIMEText(result, 'html', 'utf-8'))

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
