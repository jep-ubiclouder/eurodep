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
def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        eurodep.cwd('./OUT/IMG/')
        truc = eurodep.nlst('./OIMG515%s*.CSV' % compactDate) #ftp://HOMMEDEFER@ftp.eurodep.fr/OUT/IMG/OIMG51517102400001.CSV
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]
def getMouvements(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        eurodep.cwd('./OUT/MVT/')
        truc = eurodep.nlst('./OMVT515%s*.CSV' % compactDate) #ftp://HOMMEDEFER@ftp.eurodep.fr/OUT/IMG/OIMG51517102400001.CSV
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]

if __name__ == '__main__':
    from datetime import datetime 
    now = datetime.now() - timedelta(days=1)
    
    compactDate = '%02i%02i%02i' % (now.year-2000, now.month, now.day)
    
    
    print(compactDate)
    ## sauvegarde des fichiers mouvempent
    mvtFiles =  getMouvements(compactDate)
    # telecharger le fichier image
    fn = getfromFTP(compactDate)
    if not fn:
        import sys
        sys.exit()
        # fn = './OIMG51517102400001.CSV'
        # return False
    csvFile =  open(fn,'r') 
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    byCode = {}
    tobeDel = []
    
    
    qryProd= 'select id,ProductCode from Product2'
    res = sf.query_all(qryProd)
 
    for r in res['records']:
        if r['ProductCode'] not in byCode.keys():
            byCode[r['ProductCode']] = r['Id']
            tobeDel.append({'Id': r['Id']})
    
    ## on efface les records de stock   
    ## print(tobeDel)     
    ## sf.bulk.Stock_eurodep__c.delete(tobeDel)
    qrySTockEuro = "select id from Stock_eurodep__c"
    res = sf.query_all(qrySTockEuro)
    tobeDel = []
    for r in res['records']:
        tobeDel.append({'Id': r['Id']})
    sf.bulk.Stock_eurodep__c.delete(tobeDel)
    
    now = datetime.now() - timedelta(days=1)
    anneeEnCours = now.year
    qry = """select produit__r.Id,CALENDAR_YEAR(date_de_commande__c) , sum(Quantite__c) from Commande__c  where produit__r.Id != null and Compte__r.Id !='0010Y00000rs3auQAA' and CALENDAR_YEAR(date_de_commande__c)> %s GROUP BY produit__r.Id,CALENDAR_YEAR(date_de_commande__c)"""%(anneeEnCours-2)
    resConso = sf.query(qry)
    updateConso = []
    byId ={}
    for r in resConso['records']:
        print(r)
        if r['Id'] not in byId.keys():
            byId[r['Id']] ={'Id':r['Id'], 'Stock_eurodep_total__c':0,'Conso_Mensuelle_annee_Courante__c':1,'Conso_Mensuelle_N_1__c':1} 
        
        if r['expr0'] == anneeEnCours:
            byId[r['Id']]['Conso_Mensuelle_annee_Courante__c'] =float(r['expr1'])/now.month
        else:
            byId[r['Id']]['Conso_Mensuelle_N_1__c'] =float(r['expr1'])/12
   
    ## et on les reintroduit
    for l in csvFile.readlines():
        
        ligne = l[:-1]
        rec = ligne.split(';')
        acl =  rec[2]
        des = rec[4]
        lot= rec[5]
        if len(rec[7])==8:
            ddp = '%04s-%02s-%02s'%(rec[7][-4:],rec[7][2:4],rec[7][:2])
        else:
            ddp = '2999-12-31'
        statut = rec[9]
        if statut != 'A':
            continue
        qte = rec[10]
        qteAll = rec[11]
        keyforupsert=acl+lot
        if acl in byCode.keys():
            record={'Lot__c':lot,'Produit__c':byCode[acl],'Qte_allouee__c':qteAll,'Unites_en_stock__c':qte,'name':keyforupsert,'Peremption__c':ddp}
            # print(record)
            ## print(keyforupsert,des,qte,acl,lot,byCode[acl])
            reponse = sf.Stock_eurodep__c.upsert('KeyForUpsert__c/%s' % keyforupsert,record, raw_response=True)
            if byCode[acl] not in byId.keys():
                byId[byCode[acl]] = {'Id':byCode[acl], 'Stock_eurodep_total__c':1,'Conso_Mensuelle_annee_Courante__c':1,'Conso_Mensuelle_N_1__c':1} 
             
            byId[byCode[acl]]['Stock_eurodep_total__c'] += int(qte.split('.')[0])
            if acl=='SUD012':
                
                print(qte,int(qte.split('.')[0]),byId[byCode[acl]]['Stock_eurodep_total__c'],byId[byCode[acl]])   
        else:
            print(keyforupsert,des,qte,acl,lot,'ERROR')
            
    import pprint
    pp = pprint.PrettyPrinter(width=41, compact=True)        
    for k in byId.keys():
        updateConso.append(byId[k])
        # print(updateConso)
        if k =='01t0Y000001FrcjQAC':
            pp.pprint(byId[k])
    
    
    if len(updateConso)>0:
        sf.bulk.Product2.update(updateConso) 
