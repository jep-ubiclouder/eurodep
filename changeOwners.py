'''
Created on 06/11/2018
@author: jean-eric preis
'''
from simple_salesforce import (
    Salesforce,
    SalesforceAPI,
    SFType,
    SalesforceError,
    SalesforceMoreThanOneRecord,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceMalformedRequest
)

import sys
from _datetime import timedelta
from datetime import date
from ftplib import FTP, all_errors

import codecs
import os.path
import csv

import pprint


if __name__ == '__main__':
    sf = Salesforce(username='projets@homme-de-fer.com',
                    password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    cpt = 1
    buff = []
    LB = '0050Y000000xvJFQAY'
    qry = 'select id from Lead'
    records = sf.query_all(qry)['records']
    taille = len(records)
    for r in records:
        r['OwnerId'] = LB
        buff.append(r)
        if len(buff) > 700:
            sf.bulk.Lead.update(buff)
            buff = []
            cpt += 1
            print('batch', cpt, 'sur', taille//700)
    if len(buff) > 0:
        sf.bulk.Lead.update(buff)

    cpt = 1
    buff = []
    qry = 'select id from Contact'
    records = sf.query_all(qry)['records']
    taille = len(records)
    for r in records:
        r['OwnerId'] = LB
        buff.append(r)
        if len(buff) > 700:
            sf.bulk.Contact.update(buff)
            buff = []
            cpt += 1
            print('batch', cpt, 'sur', taille//700)
    if len(buff) > 0:
        sf.bulk.Contact.update(buff)

    buff = []
    cpt = 1
    qry = 'select id from Commande__c'
    records = sf.query_all(qry)['records']
    taille = len(records)
    for r in records:
        r['OwnerId'] = LB
        buff.append(r)
        if len(buff) > 700:
            sf.bulk.Commande__c.update(buff)
            buff = []
            cpt += 1
            print('batch', cpt, 'sur', taille//700)
    if len(buff) > 0:
        sf.bulk.Commande__c.update(buff)

  
