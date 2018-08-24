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
if __name__=='__main__':
    byCodeLabo = []
    
    
    with open("./test_newFormat.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # print(row);
            if row['Code article laboratoire'] not in byCodeLabo:
                byCodeLabo.append(row['Code article laboratoire'])
    print(byCodeLabo)
    qry = 'select id, ProductCode from  Product2 where ProductCode in ('+','.join(["\'%s\'" % cp for cp in byCodeLabo]) +')'
    print(qry)
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    result = sf.query(qry)
    records =  result['records']
    for r in records:
        print(r)
    
        
    """
    Code laboratoire;
    Type de facture;
    N° de facture;
    N° ligne de facture;
    Date de facture;
    N° de commande Eurodep;
    Date de commande;
    Référence de commande du client;
    N° de BL Eurodep;
    Date du BL;
    Secteur;
    Code représentant;
    Nom du représentant;
    Code force de vente;
    Territoire;
    Cible du client;
    Catégorie;
    Segment;
    Code Région;
    Code Eurodep du client;
    Code CIP du client;
    Code UGA du client;
    Nom du client;
    Adresse de facturation;
    Code postal;
    Ville;
    Pays;
    Téléphone;
    Fax;
    Groupement du client;
    Code article Eurodep;
    Code article laboratoire;
    EAN article;
    Désignation article;
    Mouvement de stock;
    Quantité facturé;
    Prix unitaire brut;
    Prix unitaire net;
    Montant total de la ligne;
    Poids facturé;
    Taux de TVA;
    Taux de remise;
    Référence ligne de commande 1;
    Référence ligne de commande 2;
    Référence de vente de la commande;
    """
    
    
    
