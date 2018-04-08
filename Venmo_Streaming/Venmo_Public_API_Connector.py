# Venmo Public API Connector

## Importing the required packages
import json
import requests
import datetime
import gzip
import sys
import time
import os
import getpass
from simplecrypt import decrypt

# Password Integration
master_password = getpass.getpass()

# Email Integration
sys.path.append('/home/gtc/Desktop/Resources')
from Email_Integration import send_mail
from passwords_encrypted import Gmail as email_act
email_account = email_act['email']
email_password = decrypt(master_password,email_act['password']).decode('utf-8')

## Pointing to the Venmo Public API
page = "https://venmo.com/api/v5/public"

## Opening the GZIP JSON file to write to
file_date = datetime.date.today()
outfilename = 'Venmo_Public_'+str(file_date)+".json.gz"

# Checking for exisiting file, otherwise write to a new file
if outfilename in os.listdir():
    output = gzip.open(outfilename, 'a')
    print('Appending to: '+str(outfilename))
else:
    output = gzip.open(outfilename, 'wb')
    print('Opening : '+str(outfilename))
    
# Method for keeping track of the number of records recieved as well as time to wait if we encounter an error
venmo_count = 0
break_time = 10

## While loop that writes transactions to the GZIP file
while True:
    try:
        time.sleep(2)
        current_date = datetime.date.today()
        data = requests.get(page)
        temp_json = json.loads((data.content).decode('utf-8'))['data']
        
        # For each transaction in the JSON (usually 20) write these to the GZIP file, one per line
        for record in temp_json:
            output.write(json.dumps(record).encode('utf-8'))
            output.write('\n'.encode('utf-8'))
            venmo_count += 1

        # Print the transaction count to keep tabs on the collection script
        if venmo_count%10000 ==0:
            print(str(venmo_count)+" Venmo Transactions Collected Today")
            #output.close()
            #break

        # Once it is a new day, close out the existing file and open a new file to write to. Also log the number of records captured to the data log file.
        if current_date != file_date:
            # Close the existing file 
            output.close()
            
            # Open the data logging file and write the number of records captured to the file
            data_log = open('Venmo_Data_Log.csv','a')
            data_log.write(str(file_date)+","+str(venmo_count))
            data_log.write('\n')
            data_log.close()
            
            # Open a new file and start writing to that file
            file_date = current_date
            venmo_count = 0
            outfilename = 'Venmo_Public_'+str(file_date)+".json.gz"
            output = gzip.open(outfilename, 'wb')
            print('Opening: '+str(outfilename))
            
            # Reset the break time
            break_time = 10
    
    # Error handling in case something comes up (to be improved in the future)
    except:
        print("WARNING: Connection has been lost. Unexpected error:", sys.exc_info()[0])
        break_time = break_time*2
        time.sleep(break_time)
        if break_time > 600:
            send_mail(email_account,'EMAIL@gmail.com',email_password,"Venmo Script Down","Something is wrong with the Venmo Processing Script")

    
        
