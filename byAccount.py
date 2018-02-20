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
import pprint


def checkAccount(strAccId):
    forAccount = []
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['n°client facturé']  == strAccId:
                
                ## forAccount.append(l)
                if float(l['remis ligne']) >0 : remLign=float(l['remis ligne'])
                else:  remLign=0.00
                if float(l['remise pied']) >0 : remPied=float(l['remise pied'])
                else:  remPied=0.00
                record={'remise' : (1-remLign)*(1-remPied),'prix untaire brut':float(l['prix untaire brut']),'dateCommande':l['date document']}
                forAccount.append(record)
                
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(forAccount)
    
    
    
    
    
    print(len(forAccount))
if __name__ == '__main__':
    checkAccount('007798')