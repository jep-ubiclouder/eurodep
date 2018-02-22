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
## import dateparser
from datetime import date

def checkAccount(strAccId):
    forAccount = []
    allrecords = {}
    dicoAccounts ={}
    dicoProduits = {}

    with open('./accounts.csv','r') as allAccs:
        reader  =  csv.DictReader(allAccs,delimiter=';')
        for ligne in reader : 
            dicoAccounts[ligne['Code_Client_SOFIRA__c']] = ligne
    
    with open('./products.csv','r') as allAccs:
        reader  =  csv.DictReader(allAccs,delimiter=';')
        for ligne in reader : 
            dicoProduits[ligne['ProductCode']] = ligne

    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv
        
        reader = csv.DictReader(f, delimiter=';')
        rejected={'produit':{},'client':{}}
        for l in reader:
            ## ddc = dateparser.parse(l['date document'],date_formats=['%d/%m/%Y'],settings={'DATE_ORDER': 'DMY','TIMEZONE': '-0100'})
            typeDoc = l['Type document']
            sens = 1
            if typeDoc !='F':
                sens = -1 
            try:
                (jj,mm,aaaa) = l['date document'].split('/')
            except Exception as e:
                ## print(e)
                ## print(l)
                continue    
            ddc = date(int(aaaa),int(mm),int(jj))
            ## if l['n°client facturé']  == strAccId:
            if ddc and  ddc.year ==2008:    
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
                    rejected['produit'][l['référence']] = l
                ## elif  l['N°client livré'] not in dicoAccounts.keys():
                ##     rejected['client'][l['N°client livré'] ] = l
                else:
                    try:
                        if l['N°client livré'] not in dicoAccounts.keys():
                            compte_client =  dicoAccounts['ZZZZZZ']['Id']
                            nom_compte = dicoAccounts['ZZZZZZ']['Name']
                        else:
                            compte_client = dicoAccounts[l['N°client livré']]['Id']
                            nom_compte = dicoAccounts[l['N°client livré']]['Name']
                        
                        
                        if float(l['Frais de port unique'])  > 0.00:
                            forAccount.append({  'Code_Produit_SORIFA__c' : 'POR000',
                                        'Produit__c' :  dicoProduits['POR000']['Id'],
                                        'Nom Compte': nom_compte,
                                        'Compte__c' : compte_client,
                                        'Bon_de_livraison__c' : l['Numéro document'],
                                        'Ligne__c': 0,
                                        'Prix_Brut__c' : float(l['Frais de port unique'])*sens, 
                                        'Prix_Net__c' : float(l['Frais de port unique'])*sens,
                                        'Quantite__c' :1,                                
                                        'Facture__c':l['numero BL'],
                                        'Date_de_commande__c': ddc 
                                        #  dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                    })
                        if l['prix untaire brut']:
                            record = {  'Code_Produit_SORIFA__c' : l['référence'],
                                    'Produit__c' :  dicoProduits[l['référence']]['Id'],
                                    'Nom Compte' :nom_compte,
                                    'Compte__c' :compte_client,
                                    'Bon_de_livraison__c' : l['Numéro document'],
                                    'Ligne__c': l['ligne'],
                                    'Prix_Brut__c' : float(l['prix untaire brut'])*sens, 
                                    'Prix_Net__c' : float(l['prix untaire brut']) * remise *sens,
                                    'Quantite__c' :l['quantité'],
                                    'Facture__c':l['numero BL'],
                                    'Date_de_commande__c': ddc 
                                        #  dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                }
                        else:
                            record = {  'Code_Produit_SORIFA__c' : l['référence'],
                                    'Produit__c' :  dicoProduits[l['référence']]['Id'],
                                    'Compte__c' : compte_client,
                                    'Nom Compte': nom_compte,
                                    'Bon_de_livraison__c' : l['Numéro document'],
                                    'Ligne__c': l['ligne'],
                                    'Prix_Brut__c' : 0.00, 
                                    'Prix_Net__c' : 0.00,
                                    'Quantite__c' :l['quantité'],
                                    'Facture__c':l['numero BL'],
                                    'Date_de_commande__c': ddc 
                                        #  dateparser.parse(l['date document'],date_formats=['%d/%B/%Y'],settings={'TIMEZONE': 'US/Eastern'})
                                }
                        forAccount.append(record)
                    except Exception as e:
                        print(e)
                        print(l)
    pp = pprint.PrettyPrinter(indent=4)
    ## pp.pprint(forAccount)
    print(len(rejected['client']))
    print( pp.pprint(rejected['produit']))
    
    fn = './lignes.2008.all.csv'
    ## records = sf.query_all(qry)['records']
    # print(len(records)) 
    with open(fn,'w') as csvF:
        fAccount =  csv.DictWriter(csvF,fieldnames=forAccount[0].keys(),delimiter=';')
        print(fAccount)
        fAccount.writeheader()
        
        for r in forAccount:
            fAccount.writerow(r)

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