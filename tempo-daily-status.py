#!/usr/bin/env python2
# -*- coding: utf-8 -*-
__author__ = 'themengzor'

import requests
import ConfigParser

configFile = ConfigParser.ConfigParser()

try:
    configFile.read('tds.conf')
except:
    print 'Unable to read config file ./tds.conf'
    exit(1)

globalConfig = {}
smtpConfig = {}
tempoConfig = {}

try:
    globalConfig['emails'] = configFile.get('global', 'emails')
    smtpConfig['server'] = configFile.get('smtp', 'server')
    smtpConfig['port'] = configFile.get('smtp', 'port')
    smtpConfig['security'] = configFile.get('smtp', 'security')
    smtpConfig['auth'] = configFile.get('smtp', 'auth')
    smtpConfig['login'] = configFile.get('smtp', 'login')
    smtpConfig['password'] = configFile.get('smtp', 'password')
    tempoConfig['baseurl'] = configFile.get('tempo', 'baseurl')
except:
    print 'Unable to parse config file'
    exit(1)

