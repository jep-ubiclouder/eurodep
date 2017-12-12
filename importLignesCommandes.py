#!/usr/bin/python3


import sys
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

import csv


def audit():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    allComptes =[]
    allSorifa =[]
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['n°client facturé'] not in allSorifa:
                allSorifa.append(l['n°client facturé'])
            if l['N°client livré'] not in allSorifa:
                allSorifa.append(l['N°client livré'])
            if l['référence'] not in allProduits:
                allProduits.append(l['référence'])
    print('Comptes uniques',len(allSorifa))
    print('Produits uniques',len(allProduits))
    
    print('entering Scan Accounts IDs')
    i= 0
    tmp =[]
    allSFAccIds =[]
    while(i<len(allSorifa)):
        tmp.append(allSorifa[i])
        if i%400==0:
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in tmp])+')'
            allAccountIds = sf.query_all(qryFindFromSorifa)['records']
            for r in allAccountIds:
                allSFAccIds.append(r)
            tmp=[]
            print("%s / %s Accounts "%(i,len(allSorifa)))
        i+=1

    
    qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in tmp])+')'
    allAccountIds = sf.query_all(qryFindFromSorifa)['records']
    for r in allAccountIds:
        allSFAccIds.append(r)
    print('entering Scan Products IDs')
    
    
    
    i= 0
    tmp =[]
    allSFProdIds =[]
    while(i<len(allProduits)):
        tmp.append(allProduits[i])
        if i%400==0:
            qryFindProduits =' select id, ProductCode from Product2 where ProductCode in ('+  ','.join(["\'%s\'" % c for c in tmp])+')'
            allAccountIds = sf.query_all(qryFindProduits)['records']
            for r in allAccountIds:
                allSFProdIds.append(r)
            tmp=[]
            print("%s / %s Products "%(i,len(allProduits)))
        i+=1
    qryFindProduits =' select id, ProductCode from Product2 where ProductCode in ('+  ','.join(["\'%s\'" % c for c in tmp])+')'
    allAccountIds = sf.query_all(qryFindProduits)['records']
    for r in allAccountIds:
        allSFProdIds.append(r)
    
    print('Comptes ds salesforce trouvés',len(allSFAccIds))
    print('Produits ds salesforce trouvés',len(allSFProdIds))
if __name__=='__main__':
  audit()
