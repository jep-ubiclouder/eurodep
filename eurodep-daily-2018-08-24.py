'''
Created on 24 Août 2018

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
def listeNotPresent(listeCSV,listeQuery):
    """
    retourne les membres de listeCSV qui ne sont pas dans ListeQuery
    """
    absents = []
    for item in listeCSV:
        if item not in listeQuery.keys():
            absents.append(item)
    return absents


def newSFRecord(recCSV,prodId,accId):
    retVal ={}
    retVal['Compte__c'] =accId
    retVal['Produit__c'] =prodId
    retVal['Bon_de_livraison__c'] =recCSV['N° de BL Eurodep']
    retVal['Date_de_commande__c'] ='-'.join((recCSV['Date de facture'][-4:],recCSV['Date de facture'][-6:-4],recCSV['Date de facture'][:-7]))
    retVal['Prix_Brut__c'] =recCSV['Prix unitaire brut']
    retVal['Quantite__c'] =recCSV['Quantité facturé']
    retVal['Prix_Net__c'] =recCSV['Prix unitaire net']
    retVal['Code_EAN_EURODEP__c'] =recCSV['']
    retVal['Ligne__c'] =recCSV['N° ligne de facture']
    retVal['Code_Client_EURODEP__c'] =recCSV['']
    retVal['CA_Eurodep__c'] =recCSV['']
    retVal['Reference_Client__c'] =recCSV['Référence de commande du client']
    retVal['ky4upsert__c'] =recCSV['N° de facture']+recCSV['N° ligne de facture']
    retVal['Facture__c'] =recCSV['N° de facture']
    print(retVal)
    """
    retVal['Facture__c'] =recCSV['N° de facture']
    retVal[''] =recCSV['']
    retVal[''] =recCSV['']
    retVal[''] =recCSV['']
    retVal[''] =recCSV['']
    retVal[''] =recCSV['']
    """
    return retVal

if __name__=='__main__':
    byCodeLabo = []
    byCodeClient = []
    produitsInconnus = []
    lignes =[]
    with open("./test_newFormat.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # print(row);
            if row['Code article laboratoire'] not in byCodeLabo:
                byCodeLabo.append(row['Code article laboratoire'])
            if row['Code Eurodep du client']    not in byCodeClient:
                byCodeClient.append(row['Code Eurodep du client'])
            lignes.append(row)
    print(byCodeLabo)
    qryProd = 'select id, ProductCode from  Product2 where ProductCode in ('+','.join(["\'%s\'" % cp for cp in byCodeLabo]) +')'
    print(qryProd)
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    result = sf.query_all(qryProd)
    refProduits =  result['records']
    bySORIFA = {}
    for r in refProduits:
        bySORIFA[r['ProductCode']]=r
    produitsNotinSF = listeNotPresent(byCodeLabo,bySORIFA)
    
    
    qryClient =  "select id ,Code_EURODEP__c from Account where Code_EURODEP__c in ( "+','.join(["\'%s\'" % cp for cp in byCodeClient]) +')'
    result = sf.query_all(qryClient)
    
    refClient =  result['records']
    byCLIENT = {}
    for r in refClient:
        byCLIENT[r['Code_EURODEP__c']]=r
    clientsNotinSF = listeNotPresent(byCodeClient,byCLIENT)
    
    toInsert  =[]
    for r in lignes:
        if r['Code article laboratoire'] in  bySORIFA.keys() and r['Code Eurodep du client'] in byCLIENT.keys():
            toInsert.append(newSFRecord(r,bySORIFA[r['Code article laboratoire']],byCLIENT[r['Code Eurodep du client']]))
            
            
    print(toInsert)
    
        

    
    
    
