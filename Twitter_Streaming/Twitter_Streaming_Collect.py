# -*- coding: utf-8 -*-
# Python Script to Connect to the Twitter Streaming API
# Taylor C - 4/8/2018

## This script allows us to connect to Twitter's Streaming API and store the data in GZIP JSON format for processing at a later date.

## Import the required libraries
import sys
import json
import gzip
import datetime
import time
import getpass
import os
from simplecrypt import decrypt
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

## Import Passwords - Importing Passwords from a file stored elsewhere on my computer
sys.path.append('C:/Users/GTayl/Desktop/Finance Modeling')
from passwords_encrypted import twitter_streaming as pwd
master_password = getpass.getpass()

# Email Integration
from Email_Integration import send_mail
from passwords_encrypted import Gmail as email_act
email_account = email_act['email']
email_password = decrypt(master_password,email_act['password']).decode('utf-8')


## Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = decrypt(master_password,pwd['access_token']).decode('utf-8')
ACCESS_SECRET = decrypt(master_password,pwd['access_secret']).decode('utf-8')
CONSUMER_KEY = decrypt(master_password,pwd['consumer_key']).decode('utf-8')
CONSUMER_SECRET = decrypt(master_password,pwd['consumer_secret']).decode('utf-8')

## Authorizing a session with Twitter
oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_stream = TwitterStream(auth=oauth)
iterator = twitter_stream.statuses.sample()

## Creating a File
file_date = datetime.date.today()
outfilename = 'Twitter_Random_'+str(file_date)+".json.gz"
iterfiles = os.listdir()

# Setting Tweet Counter as well as Break Time
tweet_count = 0
break_time = 10

# Opening a new file or appending to an existing file
if outfilename in iterfiles:
    output = gzip.open(outfilename, 'a')

else:
    output = gzip.open(outfilename, 'wb')

# Tweet stream iterator
while True:

    for tweet in iterator:
        try:
            
            #Get the current date (to compare to the tweet date)
            current_date = datetime.date.today()
            
            # If this is a entry refers to a deleted tweet, don't save to the file. Else write the tweet to the GZIP JSON file.
            if "delete" in tweet.keys():
                pass

            else:
                output.write(json.dumps(tweet).encode('utf-8'))
                output.write('\n'.encode('utf-8'))
                tweet_count += 1

            # To track progress, print the number of tweets collected every 10,000 tweets
            if tweet_count%100 == 0:
                print(str(tweet_count)+" Tweets Collected Today")
                #output.close()
                #break

            # If the current date is different than the tweet date, close the existing file, reset the tracking values and open a new file
            if current_date != file_date:

                # Close the existing output file
                output.close()

                # Open the data logging file and write the number of records captured to the file
                data_log = open('Twitter_Data_Log.csv','a')
                data_log.write(str(file_date)+","+str(tweet_count))
                data_log.write('\n')
                data_log.close()

                # Open a new output file
                file_date = current_date
                tweet_count = 0
                outfilename = 'Twitter_Random_'+str(file_date)+".json.gz"
                output = gzip.open(outfilename, 'wb')

                # Reset the break time
                break_time = 10

        except:
            
            # Handle Errors Passes by the API
            print("Unexpected error:", sys.exc_info()[0])
            if break_time > 600:
                send_mail(email_account,'EMAIL@gmail.com',email_password,"Twitter Script Down","The Twitter Processing script has gone down")
            break_time = break_time*2
            time.sleep(break_time)

    # Handle Errors if the internet connection dies or the API temporarily goes down
    try:
        print("WARNING: API Connection has been lost")
        break_time = break_time*2
        time.sleep(break_time)
        if break_time > 600:
            send_mail(email_account,'EMAIL@gmail.com',email_password,"Twitter Script Down","Something is wrong with the Twitter Processing script")
        iterator = twitter_stream.statuses.sample()
        
    except:
        print("WARNING: API Connection has been lost")
        break_time = break_time*2
        time.sleep(break_time)

        
