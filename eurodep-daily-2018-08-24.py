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


def envoiemailTraite(LigneTraitee):
    ''' Envoie une liste des lignes traitées'''
    import smtplib
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML = """
    Bonjour,<br/>
    Voici une liste des lignes intégrées dans le fichier du jour<br/>
    """
    tableau = '''<table>
    <tr><th>Facture </th><th>Code Eurodep </th><th> Nom </th><th> Ville </th><th> Produit </th><th> Qté</th><th> Total Net</th></tr>'''
    for r in LigneTraitee:
        # print(r)
        record = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            r['N° de facture'], r['NormalizedEURODEP'], r['Nom du client'], r['Ville'], r['Désignation article'], r['Quantité facturé'], r['Montant total de la ligne'])
        tableau += record
    tableau += '</table>'
    texteHTML += tableau

    # print(texteHTML)

    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Lignes Integrées'
    msg['From'] = 'salesforce@homme-de-fer.com'
    # , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com,    jmastio@homme-de-fer.com,    mlabarthe@homme-de-fer.com'
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s = smtplib.SMTP(host='smtp.homme-de-fer.com', port=25)
    s.login('salesforce@homme-de-fer.com', 'S@lf0rc3!')
    s.send_message(msg)
    s.quit()
    print('Email Comptes envoyé')


def envoieEmailCI(clientsInconnus):
    ''' Envoie une liste de compte qui ont un code EURODEP mais qui ne sont pas trouvé cette clef dans Salesforce'''
    import smtplib
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML = """
    Bonjour,<br/>
    Voici une liste des clients présents dans le fichier EURODEP que je n'ai pas pu trouver dans SalesForce.<br/>
    Je les ai rattaché au compte temporaire COMPTE RECUP LIGNES en attendant que vous retrouviez leurs parents <br/>
    Pouvez-vous les créer ou attacher le code Eurodep dans leur fiche, afin que je puisse ratacher les commandes.<br/>
    Le rattachement sera effectué une fois par heure entre 9 heures du matin et 14 heures tout les jours<br/>
     
    """
    tableau = '''<table>
    <tr><th>Code Eurodep </th><th> Nom </th><th> Adresse </th><th> Code Postal </th><th> Ville</th></tr>'''
    for k in clientsInconnus.keys():
        r = clientsInconnus[k]
        record = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            r['NormalizedEURODEP'], r['Nom du client'], r['Adresse de facturation'], r['Code postal'], r['Ville'])
        tableau += record
    tableau += '</table>'
    texteHTML += tableau

    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Clients Inconnus'
    msg['From'] = 'salesforce@homme-de-fer.com'
    # , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com,     jmastio@homme-de-fer.com,    mlabarthe@homme-de-fer.com'
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s = smtplib.SMTP(host='smtp.homme-de-fer.com', port=25)
    s.login('salesforce@homme-de-fer.com', 'S@lf0rc3!')
    s.send_message(msg)
    s.quit()
    print('Email Comptes envoyé')


def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        # print(eurodep.pwd())
        eurodep.cwd('OUT/ZR3/')
        ## print('OZR3515*%s.CSV' % compactDate)
        # print(eurodep.dir('*'))
        truc = eurodep.nlst('OZR3515%s*.CSV' % compactDate)
        # print(compactDate)
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]


def listeNotPresent(listeCSV, listeQuery):
    """
    retourne les membres de listeCSV qui ne sont pas dans ListeQuery
    """
    absents = []
    for item in listeCSV:
        if item not in listeQuery.keys() and item not in absents:
            absents.append(item)
    return absents


def checkUnkownClients(listCSV, listQRY):
    absents = listeNotPresent(listCSV, listQRY)
    res = []
    for item in absents:
        if (item[:-3]+'515' not in listQRY.keys()) and (item[:-3]+'000' not in listQRY.keys()) and item not in res:
            res.append(item)
    return res


def getNewClientData(clientsNotinSF, lignes):
    # for rec in ligne
    pass


def newSFRecord(recCSV, prodId, accId=None, EURODEP=None):
    """
    constriut un record a partir de la ligne du CSv
    Mappage statique
    """
    retVal = {}
    moins10 = False
    if len(recCSV['Date de facture']) < 8:
        moins10 = True

    if accId is not None:
        retVal['Compte__c'] = accId['Id']
    elif EURODEP is not None:
        retVal['Code_EAN_EURODEP__c'] = EURODEP

    retVal['Produit__c'] = prodId['Id']
    retVal['Bon_de_livraison__c'] = recCSV['N° de BL Eurodep']

    retVal['Date_de_commande__c'] = '-'.join((recCSV['Date de facture'][-4:],
                                              recCSV['Date de facture'][-6:-4], recCSV['Date de facture'][:-6]))
    if moins10:
        retVal['Date_de_commande__c'] = '-'.join((recCSV['Date de facture'][-4:],
                                                  recCSV['Date de facture'][-6:-4], '0'+recCSV['Date de facture'][:-6]))
    retVal['Prix_Brut__c'] = recCSV['Prix unitaire brut']
    retVal['Quantite__c'] = recCSV['Quantité facturé']
    retVal['Prix_Net__c'] = recCSV['Prix unitaire net']
    ## retVal['Code_EAN_EURODEP__c'] =recCSV['']
    retVal['Ligne__c'] = recCSV['N° ligne de facture']
    retVal['Code_Client_EURODEP__c'] = recCSV['NormalizedEURODEP']
    retVal['CA_Eurodep__c'] = recCSV['Montant total de la ligne']
    retVal['Reference_Client__c'] = recCSV['Référence de commande du client']
    retVal['ky4upsert__c'] = recCSV['N° de facture'] + \
        recCSV['N° ligne de facture']
    retVal['Facture__c'] = recCSV['N° de facture']
    return retVal


def processFile(fname):
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
    dujour = []

    byCodeLabo = []
    byCodeClient = []
    produitsInconnus = []
    lignes = []
    entetes = "Code laboratoire;Type de facture;N° de facture;N° ligne de facture;Date de facture;N° de commande Eurodep;Date de commande;Référence de commande du client;N° de BL Eurodep;Date du BL;Secteur;Code représentant;Nom du représentant;Code force de vente;Territoire;Cible du client;Catégorie;Segment;Code Région;Code Eurodep du client;Code CIP du client;Code UGA du client;Nom du client;Adresse de facturation;Code postal;Ville;Pays;Téléphone;Fax;Groupement du client;Code article Eurodep;Code article laboratoire;EAN article;Désignation article;Mouvement de stock;Quantité facturé;Prix unitaire brut;Prix unitaire net;Montant total de la ligne;Poids facturé;Taux de TVA;Taux de remise;Référence ligne de commande 1;Référence ligne de commande 2;Référence de vente de la commande".split(
        ";")
    print(entetes)
    with open("./work.txt", 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for r in reader:
            # print(row);
            row = {}
            i = 0
            while i < len(entetes):
                row[entetes[i]] = r[i]
                i += 1
            # print(row)

            row['NormalizedEURODEP'] = '0' * \
                (10-len(row['Code Eurodep du client'])) + \
                row['Code Eurodep du client']
            if row['Code article laboratoire'] not in byCodeLabo:
                byCodeLabo.append(row['Code article laboratoire'])
            if row['Code Eurodep du client'] not in byCodeClient:
                byCodeClient.append(row['NormalizedEURODEP'])
            lignes.append(row)
    # print(byCodeLabo)
    qryProd = 'select id, ProductCode from  Product2 where ProductCode in ('+','.join(
        ["\'%s\'" % cp for cp in byCodeLabo]) + ')'
    # print(qryProd)
    sf = Salesforce(username='projets@homme-de-fer.com',
                    password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    result = sf.query_all(qryProd)
    refProduits = result['records']
    bySORIFA = {}
    for r in refProduits:
        bySORIFA[r['ProductCode']] = r
    produitsNotinSF = listeNotPresent(byCodeLabo, bySORIFA)

    qryClient = "select id ,Code_EURODEP__c from Account where Code_EURODEP__c in ( "+','.join(
        ["\'%s000\'" % cp[:-3] for cp in byCodeClient]) + ")"

    result = sf.query_all(qryClient)
    refClient = result['records']

    byCLIENT = {}
    print(refClient)
    for r in refClient:
        byCLIENT[r['Code_EURODEP__c']] = r

    qryClient = "select id ,Code_EURODEP__c from Account where Code_EURODEP__c in ( "+','.join(
        ["\'%s515\'" % cp[:-3] for cp in byCodeClient]) + ")"
    result = sf.query_all(qryClient)
    refClient = result['records']
    for r in refClient:
        byCLIENT[r['Code_EURODEP__c']] = r
    clientsNotinSF = []

    toInsert = []
    lignesTraitees = []
    clientsInconnus = {}
    for r in lignes:
        if r['Code article laboratoire'] in bySORIFA.keys() and r['NormalizedEURODEP'][:-3]+'000' in byCLIENT.keys():
            toInsert.append(newSFRecord(
                r, bySORIFA[r['Code article laboratoire']], accId=byCLIENT[r['NormalizedEURODEP'][:-3]+'000']))
            lignesTraitees.append(r)
        elif r['Code article laboratoire'] in bySORIFA.keys() and r['NormalizedEURODEP'][:-3]+'515' in byCLIENT.keys():
            toInsert.append(newSFRecord(
                r, bySORIFA[r['Code article laboratoire']], accId=byCLIENT[r['NormalizedEURODEP'][:-3]+'515']))
            lignesTraitees.append(r)
        elif r['Code article laboratoire'] in bySORIFA.keys():
            produitsInconnus.append(r)
        else:
            if r['NormalizedEURODEP'] not in clientsInconnus:
                toInsert.append(newSFRecord(
                    r, bySORIFA[r['Code article laboratoire']], accId='0010Y000010w9dRQAQ', EURODEP=r['NormalizedEURODEP'][:-3]+'515'))
                lignesTraitees.append(r)
                clientsInconnus[r['NormalizedEURODEP']] = r
                clientsNotinSF.append(r)

    resulUpsert = sf.bulk.Commande__c.upsert(toInsert, 'ky4upsert__c')
    envoiemailTraite(lignesTraitees)
    print(len(resulUpsert), len(lignes))

    if len(clientsInconnus) > 0:
        print('Clients not in sf')
        envoieEmailCI(clientsInconnus)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")
    parser.add_argument('-r', '--reconnect',
                        action='store_true', default=False)
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)

    print(now)
    if args.reconnect is None or args.reconnect == False:
        compactDate = '%s%02i%02i' % (now.year-2000, now.month, now.day)
        print(compactDate)
        fn = getfromFTP(compactDate)
        ## fn ='correctios2017.csv'
        print('SUCCES GET', fn)
        # sys.exit()
        if fn != False:
            processFile(fn)
