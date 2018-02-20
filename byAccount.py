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
import dateparser


def checkAccount(strAccId):
    forAccount = []
    allrecords = {}
    dicoAccounts ={}
    dicoProduits = {}

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
        rejected={'produit':[],'client':[]}
        for l in reader:
            ddc = dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
            ## if l['n°client facturé']  == strAccId:
            if ddc and ddc.month<4  and ddc.year ==2008:    
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
                if l['référence']  not in  dicoProduits.keys():
                    rejected['produit'].append(l)
                elif  l['N°client livré'] not in dicoAccounts.keys():
                    rejected['client'].append(l)
                else:
                    try:
                        if l['Frais de port unique']:
                            forAccount.append({  'Code_Produit_SORIFA__c' : 'POR000',
                                        'Produit__c' :  dicoProduits['POR000'],
                                        'Compte__c' : dicoAccounts[l['N°client livré']],
                                        'Bon_de_livraison__c' : l['Numéro document'],
                                        'Ligne__c': 0,
                                        'Prix_Brut__c' : float(l['Frais de port unique']), 
                                        'Prix_Net__c' : float(l['Frais de port unique']),
                                        'Quantite__c' :1,                                
                                        'Facture__c':l['numero BL'],
                                        'Date_de_commande__c':dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                    })
                        if l['prix untaire brut']:
                            record = {  'Code_Produit_SORIFA__c' : l['référence'],
                                    'Produit__c' :  dicoProduits[l['référence']],
                                    'Compte__c' : dicoAccounts[l['N°client livré']],
                                    'Bon_de_livraison__c' : l['Numéro document'],
                                    'Ligne__c': l['ligne'],
                                    'Prix_Brut__c' : float(l['prix untaire brut']), 
                                    'Prix_Net__c' : float(l['prix untaire brut']) * remise,
                                    'Quantite__c' :l['quantité'],
                                    'Facture__c':l['numero BL'],
                                    'Date_de_commande__c':dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                }
                        else:
                            record = {  'Code_Produit_SORIFA__c' : l['référence'],
                                    'Produit__c' :  dicoProduits[l['référence']],
                                    'Compte__c' : dicoAccounts[l['N°client livré']],
                                    'Bon_de_livraison__c' : l['Numéro document'],
                                    'Ligne__c': l['ligne'],
                                    'Prix_Brut__c' : 0.00, 
                                    'Prix_Net__c' : 0.00,
                                    'Quantite__c' :l['quantité'],
                                    'Facture__c':l['numero BL'],
                                    'Date_de_commande__c':dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                }
                        forAccount.append(record)
                    except Exception as e:
                        print(e)
                        print(l)
    pp = pprint.PrettyPrinter(indent=4)
    ## pp.pprint(forAccount)
    print(len(rejected['client']))
    print(len(rejected['produit']))
    print(len(forAccount))
    
    
    pp.print(rejected)
    
    
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
    
    # print(len(forAccount))
if __name__ == '__main__':
    checkAccount('007798')