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
            qry  = 'SELECT Date_de_commande__c ,id,Year_Month__c FROM Commande__c where  Facture__c not like "F%" and Year_Month__c =' +'%s'%((annee*100)+mois)
            print(qry)
            records = sf.query_all(qry)['records']
            tobedel = []
            for r in records :
                tobedel.append({'Id':r['Id']})
            print((annee*100)+mois,'lignes:',len(tobedel))
            try:
                if len(tobedel)>0:
                    sf.bulk.Commande__c.delete(tobedel)
            except Exception as e:
                print(len(tobedel))

    

if __name__ == '__main__':
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    goDelete(sf)