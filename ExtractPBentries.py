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

import datetime
import codecs
import os.path
import csv
import xlsxwriter

def envoieMail(fileName):
    ''' Envoie une liste des lignes traitées'''
    import smtplib
    import os.path as op
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate
    from email import encoders
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML = """
    Bonjour,<br/>
    Voici le fichier pour vous permettre d'établir les tarifs.<br/>
    Ce fichier est envoyé tout les mois. Il contient les prix des tarifs qui sont en ce moment dans Salesforce.<br/>
    """
    from email.mime.text import MIMEText 
    msg = MIMEMultipart()## MIMEText(texteHTML, 'html')
    msg.attach(MIMEText(texteHTML))
    
    
    msg['Subject'] = 'Extraction fichier travail pour tarif'
    msg['From'] = 'salesforce@homme-de-fer.com'
    # , dKannengieser@asyspro.fr, adevisme@homme-de-fer.com, dk@asyspro.com'
    msg['To'] = 'lbronner@homme-de-fer.com, jep@ubiclouder.com'
    
    part = MIMEBase('application', "octet-stream")
    with open(fileName, 'rb') as file:
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition','attachment; filename='%(fileName,))
        msg.attach(part)
    # Send the message via our own SMTP server.
    ## s = smtplib.SMTP(host='smtp.dsl.ovh.net',port=25)
    s = smtplib.SMTP(host='smtp.homme-de-fer.com', port=25)
    s.login('salesforce@homme-de-fer.com', 'S@lf0rc3!')
    s.send_message(msg)
    s.quit()
    print('Email lignes envoyé')

if __name__=='__main__':
    mois=['','Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Août','Spetembre','Octobre','Novembre','Decembre']
    now = datetime.datetime.now()
    fileName= 'ElementsDeTarif-%s-%s.xlsx' %(now.year,mois[now.month])
    
    workbook =  xlsxwriter.Workbook(fileName)
    
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    sheet1 = workbook.add_worksheet()
    line = 0
    col = 0
    labels= ('Id' ,'Name','Pricebook2Id','Product2Id','UnitPrice','IsActive')
    for label in labels :
        sheet1.write_string(line,col,label)
        col += 1
    
    qry =  'select Id , Name,Pricebook2Id,Product2Id,unitPrice,IsActive from PricebookEntry where IsActive = true'
    records =  sf.query_all(qry)['records']
    for r  in records:
        print(r)
        line += 1
        col = 0
        for label in labels:
            sheet1.write(line,col,r[label])
            col += 1
    
    
    sheet2 = workbook.add_worksheet()        
    labels =('Id','Name','ProductCode')
    line = 0
    col = 0
    
    for label in labels :
        sheet2.write_string(line,col,label)
        col += 1
    qry =  'select Id , Name,ProductCode,IsActive from Product2 where IsActive = true'
    records =  sf.query_all(qry)['records']
    for r  in records:
        print(r)
        line += 1
        col = 0
        for label in labels:
            sheet2.write(line,col,r[label])
            col += 1
    
    sheet3 = workbook.add_worksheet()        
    labels =('Id','Name')
    line = 0
    col = 0
    
    for label in labels :
        sheet3.write_string(line,col,label)
        col += 1
    qry =  'select Id , Name,IsActive from PriceBook2 where IsActive = true'
    records =  sf.query_all(qry)['records']
    for r  in records:
        print(r)
        line += 1
        col = 0
        for label in labels:
            sheet3.write(line,col,r[label])
            col += 1
    workbook.close()
    envoieMail(fileName)

        
