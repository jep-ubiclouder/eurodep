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
    allrecords = {}
    dicoAccounts ={}
    dicoProduits = {}
    
    ## 
    with open('./accounts.csv','r') as allAccs:
        reader  =  csv.DictReader(allAccs,delimiter=';')
        for ligne in reader : 
            dicoAccounts[ligne['Code_Client_SOFIRA__c']] = ligne['Id']
    
    with open('./products.csv','r') as allAccs:
        reader  =  csv.DictReader(allAccs,delimiter=';')
        for ligne in reader : 
            dicoProduits[ligne['ProductCode']] = ligne['Id']
            
            
            
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['n°client facturé']  == strAccId:
                
                ## forAccount.append(l)
                if l['remis ligne'] : 
                    remLign=float(l['remis ligne'])
                else:  
                    remLign=0.00
                if l['remise pied'] : 
                    remPied=float(l['remise pied'])
                else:  
                    remPied=0.00
                    
                remise = (1-remLign)*(1-remPied)
                record = {  'Code_Produit_SORIFA__c' : l['référence'],
                            'Produit__c' :  dicoProduits[l['référence']],
                            'Compte__c' : dicoAccounts[l['N°client livré']],
                            'Bon_de_livraison__c' : l['Numéro document'],
                            'Ligne__c': l['ligne'],
                            'Prix_Brut__c' : float(l['prix untaire brut']), 
                            'Prix_Net__c' : float(l['prix untaire brut']) * remise
                            'Quantite__c' l['quantité']
                        }
                
                 ### record={'remise' : (1-remLign)*(1-remPied),'prix untaire brut':float(l['prix untaire brut']),'dateCommande':l['date document'],'puhtNet':float(l['prix untaire brut'])*(1-remLign)*(1-remPied)}
                forAccount.append(record)
                
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(forAccount)
    
    dicoChamps ={'référence':'Code_Produit_SORIFA__c',
                 'Numéro document':'Bon_de_livraison__c',
                 'date document':'Date_de_commande__c',
                 'prix untaire brut':'Prix_Brut__c',
                 'quantité':'Quantite__c',
                 'ligne' : 'Ligne__c'    
                 }
    
    """ Champs a calculer:
    Compte__c : rechercher N°client livré dans accounts.csv et retourner l'Id
    Prix_Net__c : 'puhtNet':float(l['prix untaire brut'])*(1-remLign)*(1-remPied)
    Produit__c : rechercher référence et retourner l'Id SF
    
    Si Frais de port unique different de 0 créer un record frais de port 
    """
    
    print(len(forAccount))
if __name__ == '__main__':
    checkAccount('007798')