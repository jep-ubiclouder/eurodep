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
  
    sheet1 = workbook.add_worksheet()
    line = 1
    col = 0
    labels= ('Id' ,'Name','Pricebook2Id','Product2Id','unitPrice','isActive')
    for label in labels :
        sheet1.write_string(col,line,label)
        col += 1
    
    
    
        
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry =  'select Id , Name,Pricebook2Id,Product2Id,unitPrice,isActive from PricebookEntry where isActive = true'
    records =  qf.query_all(qry)['records']
    for r  in records:
        print(r)
        line += 1
        col = 0
        for label in labels:
            sheet1.write_string(col,line,r[label])
            col += 1
    workbook.close()
        
        