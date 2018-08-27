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

def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        eurodep.cwd('OUT/ZR3')
        truc = eurodep.nlst('OZR3515*%s.CSV' % compactDate)
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]

def listeNotPresent(listeCSV,listeQuery):
    """
    retourne les membres de listeCSV qui ne sont pas dans ListeQuery
    """
    absents = []
    for item in listeCSV:
        if item not in listeQuery.keys() and item not in absents:
            absents.append(item)
    return absents

def checkUnkownClients(listCSV,listQRY):
    absents =listeNotPresent(listCSV,listQRY)
    res = []
    for item in absents:
        if (item[:-3]+'515' not in listQRY.keys()) and (item[:-3]+'000' not in listQRY.keys()) and item not in res:
             res.append(item)
    return res

def getNewClientData(clientsNotinSF,lignes):
    # for rec in ligne
    pass

def newSFRecord(recCSV,prodId,accId):
    """
    constriut un record a partir de la ligne du CSv
    Mappage statique
    """
    retVal ={}
    moins10= False
    if len(recCSV['Date de facture'])<8:
        moins10=True
    retVal['Compte__c'] =accId['Id']
    retVal['Produit__c'] =prodId['Id']
    retVal['Bon_de_livraison__c'] =recCSV['N° de BL Eurodep']
    
    retVal['Date_de_commande__c'] ='-'.join((recCSV['Date de facture'][-4:],recCSV['Date de facture'][-6:-4],recCSV['Date de facture'][:-6]))
    if moins10:
        retVal['Date_de_commande__c'] ='-'.join((recCSV['Date de facture'][-4:],recCSV['Date de facture'][-6:-4],'0'+recCSV['Date de facture'][:-6]))
    retVal['Prix_Brut__c'] =recCSV['Prix unitaire brut']
    retVal['Quantite__c'] =recCSV['Quantité facturé']
    retVal['Prix_Net__c'] =recCSV['Prix unitaire net']
    ## retVal['Code_EAN_EURODEP__c'] =recCSV['']
    retVal['Ligne__c'] =recCSV['N° ligne de facture']
    retVal['Code_Client_EURODEP__c'] =recCSV['NormalizedEURODEP']
    retVal['CA_Eurodep__c'] =recCSV['Montant total de la ligne']
    retVal['Reference_Client__c'] =recCSV['Référence de commande du client']
    retVal['ky4upsert__c'] =recCSV['N° de facture']+recCSV['N° ligne de facture']
    retVal['Facture__c'] =recCSV['N° de facture']
    return retVal

if __name__=='__main__':
    
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")
    parser.add_argument('-r', '--reconnect', action='store_true', default=False)
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
    
    
    print(now)    
    if args.reconnect is None or args.reconnect == False:
        compactDate = '%s%02i%02i' % (now.year, now.month, now.day)
        fn = getfromFTP(compactDate)
        print(fn)
        sys.exit()
        if fn != False:
            processFile(fn)
    
    byCodeLabo = []
    byCodeClient = []
    produitsInconnus = []
    lignes =[]
    with open("./test_newFormat.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # print(row);
            row['NormalizedEURODEP']='0'*(10-len(row['Code Eurodep du client']))+row['Code Eurodep du client']
            if row['Code article laboratoire'] not in byCodeLabo:
                byCodeLabo.append(row['Code article laboratoire'])
            if row['Code Eurodep du client']    not in byCodeClient:
                byCodeClient.append(row['NormalizedEURODEP'])
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
    
    
    qryClient =  "select id ,Code_EURODEP__c from Account where Code_EURODEP__c in ( "+','.join(["\'%s000\'" % cp[:-3] for cp in byCodeClient]) +")" 
    
    print(qryClient)
    result = sf.query_all(qryClient)
    ## print(qryClient)
    refClient =  result['records']
    
    byCLIENT = {}
    print(refClient)
    for r in refClient:
        byCLIENT[r['Code_EURODEP__c']]=r
    
    qryClient =  "select id ,Code_EURODEP__c from Account where Code_EURODEP__c in ( "+','.join(["\'%s515\'" % cp[:-3] for cp in byCodeClient]) +")" 
    
    ## print(qryClient)
    result = sf.query_all(qryClient)
    ## print(qryClient)
    refClient =  result['records']
    for r in refClient:
        byCLIENT[r['Code_EURODEP__c']]=r
    clientsNotinSF = checkUnkownClients(byCodeClient,byCLIENT)
    
    toInsert  =[]
    for r in lignes:
        if r['Code article laboratoire'] in  bySORIFA.keys() and r['NormalizedEURODEP'] in byCLIENT.keys():
            toInsert.append(newSFRecord(r,bySORIFA[r['Code article laboratoire']],byCLIENT[r['NormalizedEURODEP']]))
            
            
    print(clientsNotinSF)
    print(produitsNotinSF)
    if len(clientsNotinSF)>0:
        getNewClientData(clientsNotinSF,lignes)

    
        

    
    
    
