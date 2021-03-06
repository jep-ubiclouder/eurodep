#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 11 juillet 2017

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

def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        truc = eurodep.nlst('*%s.csv' % compactDate)
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]
def envoiemailTraite(LigneTraitee):
    ''' Envoie une liste des lignes traitées'''
    import smtplib
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML= """
    Bonjour,<br/>
    Voici une liste des lignes intégrées dans le fichier du jour<br/>
    """  
    tableau = '''<table>
    <tr><th>Facture </th><th>Code Eurodep </th><th> Nom </th><th> Ville </th><th> Produit </th><th> Qté</th><th> Total Net</th></tr>'''
    for r in LigneTraitee:
        
        record =  "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r['NOFAC'],r['CODCLI'],r['NOM'],r['VILLE'],r['DES'],r['QTE'],r['TOTNET'])
        tableau += record
    tableau +='</table>'
    texteHTML += tableau
     
    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Lignes Integrées'
    msg['From'] = 'salesforce@homme-de-fer.com' 
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com,    jmastio@homme-de-fer.com,    mlabarthe@homme-de-fer.com' ## , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s =  smtplib.SMTP(host='smtp.homme-de-fer.com',port=25)
    s.login('salesforce@homme-de-fer.com','S@lf0rc3!')
    s.send_message(msg)
    s.quit()
    print('Email Comptes envoyé')
    

def envoieEmailAnomalieProduit(Liste):
    import smtplib
    ''' Envoie une liste des anomalie de EAN survenues lors de l'import Eurodep'''
    ## [r['EAN ART'],r['DES'],r['NOFAC'],r['LIGNE FAC']]
    texteHTML="""
    Bonjour,<br/>
    Voici une liste des anomalies en rapport aux Codes EAN survenus lors de l'importaion EURODEP de ce jour.<br/>
    Le rattachement sera effectué une fois par heure entre 9 heures du matin et 14 heures tout les jours<br/>
    """
    tableau = '''<table>
    <tr><th>Code Eurodep </th><th> Description </th><th> Facture </th><th> Ligne  </th></tr>'''
    for r in Liste:
        record =  "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r[0],r[1],r[2],r[3])
        tableau += record
    tableau +='</table>'
    texteHTML += tableau
    
    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'EAN Inconnus'
    msg['From'] = 'salesforce@homme-de-fer.com' 
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com,    jmastio@homme-de-fer.com,    mlabarthe@homme-de-fer.com' ## , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s =  smtplib.SMTP(host='smtp.homme-de-fer.com',port=25)
    s.login('salesforce@homme-de-fer.com','S@lf0rc3!')
    s.send_message(msg)
    print('Email EAN envoyé')
    
def envoieEmailCI(clientsInconnus):
    ''' Envoie une liste de compte qui ont un code EURODEP mais qui ne sont pas trouvé cette clef dans Salesforce'''
    import smtplib
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML= """
    Bonjour,<br/>
    Voici une liste des clients présents dans le fichier EURODEP que je n'ai pas pu trouver dans SalesForce.<br/>
    Je les ai rattaché au compte temporaire COMPTE RECUP LIGNES en attendant que vous retrouviez leurs parents <br/>
    Pouvez-vous les créer ou attacher le code Eurodep dans leur fiche, afin que je puisse ratacher les commandes.<br/>
    Le rattachement sera effectué une fois par heure entre 9 heures du matin et 14 heures tout les jours<br/>
     
    """  
    tableau = '''<table>
    <tr><th>Code Eurodep </th><th> Nom </th><th> Adresse </th><th> Code Postal </th><th> Ville</th></tr>'''
    for k in clientsInconnus.keys():
        r=clientsInconnus[k]
        record =  "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r[0],r[1],r[2],r[3],r[4])
        tableau += record
    tableau +='</table>'
    texteHTML += tableau
    
    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Lignes Integrées'
    msg['From'] = 'salesforce@homme-de-fer.com' 
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com,     jmastio@homme-de-fer.com,    mlabarthe@homme-de-fer.com' ## , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s =  smtplib.SMTP(host='smtp.homme-de-fer.com',port=25)
    s.login('salesforce@homme-de-fer.com','S@lf0rc3!')
    s.send_message(msg)
    s.quit()
    print('Email Comptes envoyé')
    

def processFile(fname):

    # instanciation de l'objet salesforce
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    # initialisation des divers tableau pour filtrage
    codes_cli = []
    eans = []
    arts = []
    connus = []

    byCODCLI = {}
    byEAN = {}
    byACL = {}
    entetesClientsInconnus = {'NOM': 'Nom', 'ADRESSE': 'Adresse', 'CP': 'Code postal', 'VILLE': 'Ville', 'CODCLI': 'Code EURODEP'}

    # Eurodep ne fournit pas les fichier en UTF-8 !, je m'en occupe moi meme
    sourceEncoding = "iso-8859-1"
    source = fname
    BLOCKSIZE = 1048576  # or some other, desired size in bytes
    with codecs.open(fname, "r", sourceEncoding) as sourceFile:
        with codecs.open("./work.txt", "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)
    # Je travaille dans le fichier temporaire qui en UTF8
    dujour=[]
    with open("./work.txt", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        # dans chaque ligne je repère le champ clef
        for row in reader:
            dujour.append(row)
            # CODCLI est le numero EURODEP
            if row['CODCLI'] not in codes_cli:
                codes_cli.append("%s" % row['CODCLI'])
                byCODCLI[row['CODCLI']] = []
            # ART est le code ACL
            if row['ART'] not in arts:
                arts.append(row['ART'])
                byACL[row['ART']] = []
            # EAN
            if row['EAN ART'] not in eans:
                eans.append(row['EAN ART'])
                byEAN[row['EAN ART']] = []
            # je popule les divers dictionnaires
            byCODCLI[row['CODCLI']].append(row)
            byEAN[row['EAN ART']].append(row)
            byACL[row['ART']].append(row)
            
    # print(codes_cli)

    qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join([
        "\'%s\'" % c for c in codes_cli]) + ')'
    print(qry_code_eurodep)
    les_ids = sf.query(qry_code_eurodep)
    byEurodep = {}
    byEAN = {}
    #byACL = {}
    for acc in les_ids['records']:
        print(acc)
        connus.append(acc['Code_EURODEP__c'])
        byEurodep[acc['Code_EURODEP__c']] = acc['Id']
    ## clientsInconnus = findUnknownItems(connus, codes_cli)
    print(byEurodep)
    oldEurodep000 =[]
    for c in codes_cli :
        ## print(c)
        if c not in byEurodep.keys():
            oldEurodep000.append(c[:-3]+'000')
    if len(oldEurodep000)>0:        
        qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join([
            "\'%s\'" % c for c in oldEurodep000]) + ')'
    
        les_ids = sf.query(qry_code_eurodep)
        for acc in les_ids['records']:
            print(acc)
            connus.append(acc['Code_EURODEP__c'][:-3]+'515')
            byEurodep[acc['Code_EURODEP__c'][:-3]+'515'] = acc['Id']
 
    qry_code_byEAN = 'select id,name,EAN__C from Product2 where EAN__c  in ('+','.join([
        "\'%s\'" % c for c in eans]) + ')'
    
    les_codes_produits = sf.query(qry_code_byEAN)
    for acc in les_codes_produits['records']:
        byEAN[acc['EAN__c']] = acc['Id'] 
    print(byEAN)
    
    CompteInconnus  = {}
    EANInconnus = []
    LigneTraitee =[]
    for r in dujour:
    # print(r)
        if r['CODCLI'] in byEurodep.keys() and r['EAN ART'] in byEAN.keys():
            tmp ={}
            tmp['Facture__c']=r['NOFAC']
            tmp['Bon_de_livraison__c']=r['NOCDE']
            tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            tmp['Prix_Brut__c'] = r['PBRUT']
            tmp['Quantite__c'] = r['QTE']
            tmp['Prix_Net__c'] = r['PNET']
            tmp['Produit__c'] = byEAN[r['EAN ART']]
            tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['LIGNE FAC']
            tmp['Compte__c'] =  byEurodep[r['CODCLI']]
            
            tmp['CA_Eurodep__c'] = r['TOTNET']
            keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
            
            ## print(tmp)
            try:
                LigneTraitee.append(r)
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
                
            except all_errors as e:
                print(e)
        elif r['CODCLI'] in byEurodep.keys() and r['EAN ART'] not in byEAN.keys():
            tmp ={}
            tmp['Facture__c']=r['NOFAC']
            tmp['Bon_de_livraison__c']=r['NOCDE']
            tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            tmp['Prix_Brut__c'] = r['PBRUT']
            tmp['Quantite__c'] = r['QTE']
            tmp['Prix_Net__c'] = r['PNET']
            tmp['Code_EAN_EURODEP__c'] = r['EAN ART']
            tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['LIGNE FAC']
            tmp['Compte__c'] =  byEurodep[r['CODCLI']]
            tmp['CA_Eurodep__c'] = r['TOTNET']
            keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            
            EANInconnus.append([r['EAN ART'],r['DES'],r['NOFAC'],r['LIGNE FAC']])
                    
        elif r['CODCLI'] not  in byEurodep.keys() and r['EAN ART']  in byEAN.keys(): 
            tmp ={}
            tmp['Facture__c']=r['NOFAC']
            tmp['Bon_de_livraison__c']=r['NOCDE']
            tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            tmp['Prix_Brut__c'] = r['PBRUT']
            tmp['Quantite__c'] = r['QTE']
            tmp['Prix_Net__c'] = r['PNET']
            tmp['Produit__c'] = byEAN[r['EAN ART']]
            tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['LIGNE FAC']
            tmp['Code_Client_EURODEP__c'] =  r['CODCLI']
            tmp['CA_Eurodep__c'] = r['TOTNET']
            tmp['Compte__c'] ='0010Y000010w9dRQAQ'
            keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
            
            if  r['CODCLI'] not in CompteInconnus.keys():
                CompteInconnus[r['CODCLI']] = [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
            ## print(tmp)
            try:
                LigneTraitee.append(r)
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)                
        else:
            tmp ={}
            tmp['Facture__c']=r['NOFAC']
            tmp['Bon_de_livraison__c']=r['NOCDE']
            tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            tmp['Prix_Brut__c'] = r['PBRUT']
            tmp['Quantite__c'] = r['QTE']
            tmp['Prix_Net__c'] = r['PNET']
            tmp['Code_EAN_EURODEP__c'] = r['EAN ART']
            tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['LIGNE FAC']
            tmp['Code_Client_EURODEP__c'] =  r['CODCLI']
            tmp['CA_Eurodep__c'] = r['TOTNET']
            keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            
                    
    print(EANInconnus)
    print(CompteInconnus)

        
                 
    pathFile = './ComptesInconnus.txt'
    cpteDump =  open(pathFile,'a')
    for k in CompteInconnus.keys():
        cpteDump.write(CompteInconnus[k][0] + '\n')
    cpteDump.close()
    
    if len(LigneTraitee)>0:
        envoiemailTraite(LigneTraitee)
        
    ## TODO
    ## Dump les CompteInconnus dans un fichier COMPTESINCONNU a la fin
    if len(CompteInconnus.keys())>0:
        envoieEmailCI(CompteInconnus)
    if len(EANInconnus)>0:
        envoieEmailAnomalieProduit(EANInconnus)
def TryConnectComptes():
    pathFile = './ComptesInconnus.txt'
    stackTrouves =[]
    cpteDump = open(pathFile,'r')
    ComptesInconnus =[]
    Original = []
    for l in cpteDump.readlines():
        id=l[:-1] 
        racine=id[:-3]
        if id not in Original:
            Original.append(id)
            ComptesInconnus.append(racine+'000')
            ComptesInconnus.append(racine+'515')
    if len(ComptesInconnus)>0:
        sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
        qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join(["\'%s\'" % c for c in ComptesInconnus]) + ')'
        result = sf.query(qry_code_eurodep)
        records =  result['records']
        stackTrouves =[]
        if len(records)>0:
            bulkUpdates= []
            for r in records:
                AccId = r['Id']
                qryUpdateLignes = ' select id, Ligne__c, Code_Client_EURODEP__c,Compte__c from Commande__c where  Code_Client_EURODEP__c=\'%s\' '%r['Code_EURODEP__c']
                resUpdate = sf.query(qryUpdateLignes)
                
                for rec in resUpdate['records']:
                    bulkUpdates.append({'Id': rec['Id'],'Compte__c':AccId})
                    if rec['Code_Client_EURODEP__c'][:-3] not in stackTrouves:
                        stackTrouves.append(rec['Code_Client_EURODEP__c'][:-3])                    
            print(bulkUpdates)
            if(len(bulkUpdates))>0:
                sf.bulk.Commande__c.update(bulkUpdates)
    cpteDump.close()
    
    cpteDump = open(pathFile,'w')
    for s in Original:
        if s[:-3] not in stackTrouves:
            cpteDump.write(s+'\n')
    cpteDump.close()
    print('reconcilé')
    print(bulkUpdates)
def PruneAndGraft():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry = 'select id,Doublon__c,Compte_de_rattachement__c from Account where Doublon__c=true'
    result = sf.query_all(qry)
    
    oldIds =[]
    mapIds = {}
    deletions = []
    for r in result['records']:
        newId = r['Compte_de_rattachement__c']
        oldId = r['Id']
        oldIds.append(oldId)
        deletions.append({'Id':oldId})
        mapIds[oldId] = newId
    if len(oldIds)>0:
        updateCommandes= []
        qryCommandes = ' select id, Compte__c from Commande__c where  Compte__c in ('+','.join(["\'%s\'" % c for c in oldIds]) + ')'
        resCommandes = sf.query_all(qryCommandes)
        
        for r in resCommandes['records']:
            updateCommandes.append({'Id':r['Id'],'Compte__c':mapIds[r['Compte__c']]} )
        if len(updateCommandes) :
            res = sf.bulk.Commande__c.update(updateCommandes)
        qryContacts = 'select id, AccountId from contact where AccountId in (' + ','.join(["\'%s\'" % c for c in oldIds]) + ')'          
        resContacts = sf.query_all(qryContacts)
        updateContacts = []
        for r in resContacts['records']:
            updateContacts.append({'Id':r['Id'],'AccountId':mapIds[r['AccountId']]})
        if len(updateContacts)> 0:
            sf.bulk.Contact.update(updateContacts)
def connectLignes():
    """ Essai de reconnecter les lignes aux comptes"""
    
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    #sf = Salesforce(username=config['DEFAULT']['username'], password=config['DEFAULT']['password'], security_token=config['DEFAULT']['security_token'])
    sf = Salesforce(username='projets@homme-de-fer.com',
                    password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry = 'select id, Code_Client_EURODEP__c,Compte__c from commande__c where Code_Client_EURODEP__c !=null  and Compte__c = null' 
    allEurodep = []
    Lignes =  sf.query_all(qry)['records']
    for r in Lignes:
        if r['Code_Client_EURODEP__c'] not in allEurodep:
            allEurodep.append(r['Code_Client_EURODEP__c'][:-3]+'000')
            allEurodep.append(r['Code_Client_EURODEP__c'][:-3]+'515')
    print(len(allEurodep))  
    
    # on cherche les id
    qryAccounts = 'select id, Code_EURODEP__c from Account where Code_EURODEP__c in (' +','.join(["\'%s\'" % c for c in allEurodep]) + ')'
    Comptes =  sf.query_all(qryAccounts)['records']
    dictComptes = {}
    for r in Comptes:
        dictComptes[r['Code_EURODEP__c']] = r['Id']
    forUpdate =[]
    for r in Lignes:
        clef = ''
        if r['Code_Client_EURODEP__c'][:-3]+'515' in dictComptes.keys():
            clef = r['Code_Client_EURODEP__c'][:-3]+'515'
        if r['Code_Client_EURODEP__c'][:-3]+'000' in dictComptes.keys():
            clef = r['Code_Client_EURODEP__c'][:-3]+'000'
        if clef != '':
            forUpdate.append({'Id':r['Id'],'Compte__c':dictComptes[clef]})
    print(len(forUpdate))
    print(forUpdate[-6:])
    res = sf.bulk.Commande__c.update(forUpdate) 
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")
    parser.add_argument('-r', '--reconnect', action='store_true', default=False)
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
        
    if args.reconnect is None or args.reconnect == False:
        compactDate = '%s%02i%02i' % (now.year, now.month, now.day)
        fn = getfromFTP(compactDate)
        if fn != False:
            processFile(fn)
    else:
        # TryConnectComptes()
        connectLignes()
        PruneAndGraft()
