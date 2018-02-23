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

def goDelete(sf):
    
    for annee in range(2006,2011):
        for mois in range(1,13):
            qry  = 'SELECT Date_de_commande__c ,id,Year_Month__c,Facture__c FROM Commande__c where  Year_Month__c =' +'%s'%((annee*100)+mois)
            print(qry)
            records = sf.query_all(qry)['records']
            tobedel = []
            for r in records :
                if r['Facture__c'][0].isalpha():  ## si le premie char de facture__c est une lettre => vient de EURODEP
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
    with open('./lignes.2008.all.csv','r') as allRecords:
        reader  =  csv.DictReader(allAccs,delimiter=';')
        for r in reader:
            if r['Date_de_commande__c'][:7]=='2008-01':
                lai ={}
                for k in r.keys():
                    if k in fieldsToInsert:
                        lai[k] = r[k]
                arrInsertions.append(lai)
                if len(arrInsertions) > 150:
                    try :
                        sf.bulk.commande__c.insert(arrInsertions)
                        arrInsertions = []
                    except Exception as e:
                        print('Erreur ', e)
                        sys.exit()
        try :
            sf.bulk.commande__c.insert(arrInsertions)
            arrInsertions = []
        except Exception as e:
            print('Erreur ', e)
            sys.exit()                    
if __name__ == '__main__':
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    doIt(sf)
    
    ## goDelete(sf)