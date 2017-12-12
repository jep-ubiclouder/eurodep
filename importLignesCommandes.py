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
import json

def audit():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    allComptes =[]
    allSorifa =[]
    allLignes ={}
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['n°client facturé'] not in allSorifa:
                allSorifa.append(l['n°client facturé'])
            if l['N°client livré'] not in allSorifa:
                allSorifa.append(l['N°client livré'])
            if l['référence'] not in allProduits:
                allProduits.append(l['référence'])
                
            if l['n°client facturé'] not in allLignes.keys():
                allLignes[l['n°client facturé']]={}
                allLignes[l['n°client facturé']]['data']=l
                allLignes[l['n°client facturé']]['type']='F'
            if l['N°client livré'] not in allLignes.keys():
                allLignes[l['N°client livré']] ={}
                allLignes[l['N°client livré']]['data']=l
                allLignes[l['N°client livré']]['type']='L'
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
    jsonAllAcc = json.dumps(allSFAccIds)
    jsonAllPro = json.dumps(allSFProdIds)
    
    with open('./Accounts.json', 'w') as f:
        f.write(jsonAllAcc)
    with open('./Products.json', 'w') as f:
        f.write(jsonAllPro)
    
    
    tmpFoundAcc =[]
    for r in allSFAccIds:
        tmpFoundAcc.append(r['Code_Client_SOFIRA__c'])
        
    notfound =[]
    cpte = 0
    for  idAcc in  allLignes.keys():
        if idAcc not in  tmpFoundAcc:
            cpte +=1
            notfound.append(idAcc)
            l = allLignes[idAcc]['data']
            if allLignes[idAcc]['type'] =='F': 
                print(idAcc ,l['F raison sociale'],l['F localité'],l['F ville'])
            else:
                print(idAcc ,l['L raison sociale'],l['L localité'],l['L ville'])
    qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Lead where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in notfound])+')'
    FoundLeads = sf.query_all(qryFindFromSorifa)['records'] 
    print('Leads trouves dans SF ',len(FoundLeads))
    print('should be ',qryFindFromSorifa)
if __name__=='__main__':
  audit()
