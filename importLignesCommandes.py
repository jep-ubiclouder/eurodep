#!/usr/bin/python3


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

def audit(sf):
    ## sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    allComptes =[]
    allSorifa =[]
    allLignes ={}
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['n°client facturé'] not in allSorifa:
                allSorifa.append(l['n°client facturé'])
            if l['N°client livré'] not in allSorifa:
                allSorifa.append(l['N°client livré'])
            if l['référence'] not in allProduits:
                allProduits.append(l['référence'])
                
            if l['n°client facturé'] not in allLignes.keys():
                allLignes[l['n°client facturé']]={}
                allLignes[l['n°client facturé']]['data']=l
                allLignes[l['n°client facturé']]['type']='F'
            if l['N°client livré'] not in allLignes.keys():
                allLignes[l['N°client livré']] ={}
                allLignes[l['N°client livré']]['data']=l
                allLignes[l['N°client livré']]['type']='L'
    print('Comptes uniques',len(allSorifa))
    print('Produits uniques',len(allProduits))
    
    print('entering Scan Accounts IDs')
    i= 0
    tmp =[]
    allSFAccIds =[]
    while(i<len(allSorifa)):
        tmp.append(allSorifa[i])
        if i%400==0:
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in tmp])+')'
            allAccountIds = sf.query_all(qryFindFromSorifa)['records']
            for r in allAccountIds:
                allSFAccIds.append(r)
            tmp=[]
            print("%s / %s Accounts "%(i,len(allSorifa)))
        i+=1

    
    qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in tmp])+')'
    allAccountIds = sf.query_all(qryFindFromSorifa)['records']
    for r in allAccountIds:
        allSFAccIds.append(r)
    print('entering Scan Products IDs')
    
    
    
    i= 0
    tmp =[]
    allSFProdIds =[]
    while(i<len(allProduits)):
        tmp.append(allProduits[i])
        if i%400==0:
            qryFindProduits =' select id, ProductCode from Product2 where ProductCode in ('+  ','.join(["\'%s\'" % c for c in tmp])+')'
            allAccountIds = sf.query_all(qryFindProduits)['records']
            for r in allAccountIds:
                allSFProdIds.append(r)
            tmp=[]
            print("%s / %s Products "%(i,len(allProduits)))
        i+=1
    qryFindProduits =' select id, ProductCode from Product2 where ProductCode in ('+  ','.join(["\'%s\'" % c for c in tmp])+')'
    allAccountIds = sf.query_all(qryFindProduits)['records']
    for r in allAccountIds:
        allSFProdIds.append(r)
    
    print('Comptes ds salesforce trouvés',len(allSFAccIds))
    print('Produits ds salesforce trouvés',len(allSFProdIds))
    jsonAllAcc = json.dumps(allSFAccIds)
    jsonAllPro = json.dumps(allSFProdIds)
    
    with open('./Accounts.json', 'w') as f:
        f.write(jsonAllAcc)
    with open('./Products.json', 'w') as f:
        f.write(jsonAllPro)
    
    
    tmpFoundAcc =[]
    for r in allSFAccIds:
        tmpFoundAcc.append(r['Code_Client_SOFIRA__c'])
        
    notfound =[]
    cpte = 0
    fLeadsFound = open('./LeadFound.txt','w')
    fSorifaInconnus = open('./inconnus.txt','w')
    
    for  idAcc in  allLignes.keys():
        if idAcc not in  tmpFoundAcc and len(idAcc)>1:
            cpte +=1
            notfound.append(idAcc)
            l = allLignes[idAcc]['data']
            if allLignes[idAcc]['type'] =='F': 
                print(idAcc ,l['F raison sociale'],l['F localité'],l['F ville'])
            else:
                print(idAcc ,l['L raison sociale'],l['L localité'],l['L ville'])
                            
    qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Lead where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in notfound])+')'
    FoundLeads = sf.query_all(qryFindFromSorifa)['records']
    sorifaInLeads =[]
    for r in FoundLeads:
        sorifaInLeads.append(r['Code_Client_SOFIRA__c'])
    
    fLeadsFound = open('./LeadFound.txt','w')
    fSorifaInconnus = open('./inconnus.txt','w')
    LeadsFound =[]
    SorifaInconnus =[]
    
    for  idAcc in  allLignes.keys():
        l = allLignes[idAcc]['data']
        if allLignes[idAcc]['type'] =='F': 
            ligne = (idAcc ,l['F raison sociale'],l['F localité'],l['F ville'])
        else:
            ligne = (idAcc ,l['L raison sociale'],l['L localité'],l['L ville'])

        if idAcc in  tmpFoundAcc and len(idAcc)>1: ## trouvé dans compte  
            continue
        if idAcc in sorifaInLeads:  ## trouvé dans les Leads de SF
            fLeadsFound.write("%s;%s;%s;%s\n"%ligne)
        else:
            fSorifaInconnus.write("%s;%s;%s;%s\n"%ligne)
             
    """writer = csv.writer(fLeadsFound)
    writer.writerows(LeadsFound)         
   
    writer = csv.writer(fSorifaInconnus)
    writer.writerows(SorifaInconnus)"""
    print('Leads trouves dans SF ',len(FoundLeads))
    print('should be ',len(notfound))
    
    
def massdelete(sf ,annee, mois):
    # vu la masse de lignes a effacer, nous ferons des batchs.
    strMonth= ['','01','02','03','04','05','06','07','08','09','10','11','12']
    qry  = 'SELECT Date_de_commande__c ,id,Year_Month__c FROM Commande__c where Year_Month__c =' +'%s'%((annee*100)+mois)
    records = sf.query_all(qry)['records']
    tobedel = []
    for r in records :
        tobedel.append(r['Id']+'\n')
    
    audit = open('Effacements-%s.txt'%((annee*100)+mois),'w')
    audit.writelines(tobedel)
    audit.close()             
    print((annee*100)+mois+1,'lignes:',len(tobedel))                                              
    ## sf.bulk.delete(tobedel)


def splitBigFileByMonth():
    
    """
        Reponse;Type document;Numéro document;Numéro document-ligne;Frais de port unique;date document;n°client facturé;N°client livré;montant net HT;Montant TVA;Montant net TTC;remise pied;poids;Fraisport;codeTVAport;TVAport;numero BL;ligne;référence;désignation;quantité;prix untaire brut;prix untaire net HT;remis ligne;codeTVA;TauxTVA;Total Brut HT;Total TVA du brut;Total brut TTC;Total net HT;Total TVA du net;Total net TTC;F raison sociale;F rue;F complément;F localité;F code postal;F ville;F pays;L raison sociale;L rue;L complément;L localité;L code postal;L ville;L pays;soumis tva;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;
    """
    tmpfilenames = []
    dicoPetitsFichiers ={}
    with open('./archive_ldc.csv','r') as f: # Internet2017.csv venteshisto.csv  
        reader = csv.DictReader(f, delimiter=';')      
        for l in reader:
            (j,m,a) = l['date document'].split('/')
            fn ='Insertions-%s-%s.txt'%(a,m)
            if fn not in dicoPetitsFichiers.keys():
                dicoPetitsFichiers[fn] = csv.DictWriter(open('./'+fn,'w'),fieldnames=l.keys(),delimiter=';')
                dicoPetitsFichiers[fn].writeheader()
            dicoPetitsFichiers[fn].writerow(l)
    print(tmpfilenames,len(tmpfilenames))

def getAccounts(sf):
    qry = "select id,Code_Client_SOFIRA__c,name from account"
    fn = 'accounts.csv'
    records = sf.query_all(qry)['records']
    print(len(records))
    with open(fn,'w') as csvF:
        fAccount =  csv.DictWriter(csvF,fieldnames=['Id','Name','Code_Client_SOFIRA__c'],delimiter=';')
        print(fAccount)
        fAccount.writeheader()
        
        for r in records:
            ligne = {'Id':r['Id'],'Name':r['Name'],'Code_Client_SOFIRA__c':r['Code_Client_SOFIRA__c']} 
            fAccount.writerow(ligne)

if __name__=='__main__':
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    ## audit(sf)
    
    getAccounts(sf)
    
    """for y in range(1996, 1999):
        for m in range(1,13):
            massdelete(sf, y,m)
            pass
    splitBigFileByMonth()"""