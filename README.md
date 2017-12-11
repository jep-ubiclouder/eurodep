# eurodep
Scripts quotidiens :
eurodep-daily.py => ramene les lignes de commandes 
HdFStockqutidiens.py => parse l'etat du stock a partir des fichiers image fournis par eurodep


Utilisation:
Dans un crontab:

52 7 * * *  cd /home/salesforce/eurodep/; /usr/bin/python3 /home/salesforce/eurodep/eurpodep-daily.py 2>>/home/salesforce/log.python.txt
59 4 * * * cd /home/salesforce/eurodep/; /usr/bin/python3 /home/salesforce/eurodep/HdfStockquotidien.py 

