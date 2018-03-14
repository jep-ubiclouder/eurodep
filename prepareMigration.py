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
import csv
def goDelete(sf):
    
    for annee in range(2007,2008):
        for mois in range(1,2):
            qry  = 'SELECT Date_de_commande__c ,id,Year_Month__c,Facture__c,Bon_de_livraison__c FROM Commande__c where  Year_Month__c =' +'%s'%((annee*100)+mois)
            print(qry)
            records = sf.query_all(qry)['records']
            tobedel = []
            for r in records :
                if r['Facture__c'] is not None and r['Facture__c'][0].isalpha() :  ## si le premie char de facture__c est une lettre => vient de EURODEP
                    continue                      ## donc on efface pas. 
                tobedel.append({'Id':r['Id']})
            print((annee*100)+mois,'lignes:',len(tobedel))
            try:
                if len(tobedel)>0:
                    sf.bulk.Commande__c.delete(tobedel)
            except Exception as e:
                print(len(tobedel))

    
def doIt(sf):
    ## insertion des lignes
    fieldsToInsert = ['Compte__c','Quantite__c','Date_de_commande__c','Facture__c','Ligne__c','Prix_Net__c','Produit__c','Bon_de_livraison__c','Prix_Brut__c']
    arrInsertions = []
    nbreSent = 0
    with open('./lignes.2008.all.csv','r') as allRecords:
        reader  =  csv.DictReader(allRecords,delimiter=';')
        for r in reader:
            if int(r['Date_de_commande__c'][:4]) >=2016:
                lai ={}
                for k in r.keys():
                    if k in fieldsToInsert:
                        lai[k] = r[k]
                arrInsertions.append(lai)
                if len(arrInsertions) >= 250:
                    try :
                        print('Sending one batch ! ',nbreSent)
                        nbreSent += 1
                        sf.bulk.commande__c.insert(arrInsertions)
                        arrInsertions = []
                    except Exception as e:
                        print('Erreur ', e)
                        sys.exit()
        try :
            print('Sending remaining records ',nbreSent)
            sf.bulk.commande__c.insert(arrInsertions)
            arrInsertions = []
        except Exception as e:
            print('Erreur ', e)
            sys.exit()
            
def utilsDelete(sf):
    qry = 'SELECT CreatedDate,Date_de_commande__c,Facture__c,Id FROM Commande__c WHERE CreatedDate < 2017-04-30T05:00:00Z'
    rec =sf.query_all(qry)['records']
    tobedel=[]  
    for r in rec:
        tobedel.append({'Id':r['Id']})
    if len(tobedel)>0:
        sf.bulk.Commande__c.delete(tobedel)
                           
if __name__ == '__main__':
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    goDelete(sf)
    ## doIt(sf)
    utilsDelete(sf)
    
    ## 