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
import xlsxwriter
if __name__=='__main__':
    
    workbook =  xlsxwriter.Workbook('ElementsDeTarif.xlsx')
    
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
    labels =('Id','Name')
    line = 0
    col = 0
    
    for label in labels :
        sheet2.write_string(line,col,label)
        col += 1
    qry =  'select Id , Name,IsActive from Product2 where IsActive = true'
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

        