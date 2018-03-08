import sys
import csv
import json
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
 

if __name__ == '__main__':
    pass
    qry = 'select id, Prix_Brut__c,Prix_Net__c,Quantite__c,Remise__c ,Date_de_commande__c,Code_Produit_SORIFA__c,Facture__c,Ligne__c,C_A_Brut__c,C_A_Net__c,keyforupsert__c  from Commande__c'
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allLC =sf.query_all(qry)['records']
    byFacLig= {}
    
    allKeys=['Id', 'Prix_Brut__c','Prix_Net__c','Quantite__c','Remise__c' ,'Date_de_commande__c','Code_Produit_SORIFA__c','Facture__c','Ligne__c','C_A_Brut__c','C_A_Net__c','keyforupsert__c']
    for k in allLC[0].keys():
        allKeys.append(k)
    for r in allLC:
        if r['Facture__c'] is not None and r['Ligne__c'] is not None:
            byFacLig[r['Facture__c']+'--'+r['Ligne__c']] = r
    
    
    rec ={'xl.Code produit':'',
          'xl.Facture':'',
          'xl.Code produit':'',
          'xl.Prix_Brut' : '', 
          'xl.Prix_Net' : '',
          'xl.Ligne__c': '',
          'xl.Quantite__c' :'',
          }
    for k in rec.keys():
        allKeys.append(k)
        
    with open('./archive_ldc.csv','r') as f:     
        reader = csv.DictReader(f, delimiter=';')   
        for l in reader:
            typeDoc = l['Type document']
            sens = 1
            if typeDoc not in ('F','L') :
                sens = -1 
            
            if l['remis ligne'] : 
                remLign=float(l['remis ligne'])
            else:  
                remLign=0.00
            if l['remise pied'] : 
                remPied=float(l['remise pied'])
            else:  
                remPied=0.00
            remise = (1-remLign)*(1-remPied)
            
            try:
                tmp = float(l['prix untaire brut'])
            except Exception as e:
                l['prix untaire brut'] ='0'
            
            try:
                tmp = float(l['Frais de port unique'])
            except Exception as e:
                l['Frais de port unique'] ='0'   
            rec ={'xl.Code produit':l['référence'],
              'xl.Facture':l['numero BL'], 
              'xl.Code produit':l['référence'],
              'xl.Prix_Brut' :float(l['prix untaire brut']) *sens, 
              'xl.Prix_Net' : float(l['prix untaire brut']) * remise *sens,
              'xl.Ligne__c': l['ligne'],
              'xl.Quantite__c' :l['quantité'],
              }

            if l['numero BL']+'--'+l['ligne'] in byFacLig.keys():  
                r = byFacLig[l['numero BL']+'--'+l['ligne']]
                for k in rec.keys():
                    r[k] = rec[k]
            
            if abs(float(l['Frais de port unique']))  > 0.01:
                rec ={'xl.Code produit':'POR000',
                  'xl.Facture':l['numero BL'],
                  'xl.Code produit':l['référence'],
                  'xl.Prix_Brut' : l['Frais de port unique']*sens, 
                  'xl.Prix_Net' : l['Frais de port unique'] *sens,
                  'xl.Ligne__c': '0',
                  'xl.Quantite__c' :1,
                  }
                if l['numero BL']+'--0' in byFacLig.keys():
                    r = byFacLig[l['numero BL']+'--'+l['ligne']]
                    for k in rec.keys():
                        r[k] = rec[k]
    
    
    ## csv.DictWriter(csvF,fieldnames=forAccount[0].keys(),delimiter=';')
    with open('./controleImport.csv','w') as ctrl:
        wr = csv.DictWriter(ctrl, fieldnames = allKeys,delimiter=';')
        wr.writeheader()
        for k in byFacLig.keys():
            wr.writerow(byFacLig[k])
            ## print(byFacLig[k])