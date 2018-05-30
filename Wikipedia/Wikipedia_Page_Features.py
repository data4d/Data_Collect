# -*- coding: utf-8 -*-
"""
Created on Sat May 19 12:28:22 2018

@author: GTayl
"""
# Import the required packages
import re
import json
import requests
import time
import pandas as pd

def Page_Link_Extractor_Direct(item):
    '''
    This function returns a list of the wikipedia articles that are referenced within the text of a given wikipedia page
    
    Input: the title of a wikipeida page (as a string)
    Output: a list of the internal (wikipedia) articles that are referenced on that page
    
    '''
    
    # Replace spaces with proper url notation
    item = item.replace(" ","%20")
    
    # Define the for the Wikipedia Item of Interest
    url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&rvprop=content&titles="+str(item)
    
    # Make the request to Wikipedia
    data = requests.get(url)
    
    # Convert the returned JSON into text
    text = str(json.loads(data.content))
    
    # Define a regex and search the text using that regex to identify links within the text
    pattern = r"\[([A-Za-z0-9\s_]+)\]"
    links = re.findall(pattern,text)
    
    # Return the resulting links as a list
    return(links)
    

def Page_Link_Extractor(text):
    '''
    This function returns a list of the wikipedia articles that are referenced within the text of a given wikipedia page
    
    Input: the content of a wikipeida page (as a string)
    Output: a list of the internal (wikipedia) articles that are referenced on that page
    
    '''
    
    # Define a regex and search the text using that regex to identify links within the text
    pattern = r"\[([A-Za-z0-9\s_]+)\]"
    links = re.findall(pattern,text)
    
    # Return the resulting links as a list
    return(links)


def Get_Wiki_Page_Data(item):
    '''
    This function returns a list of the wikipedia articles that are referenced within the text of a given wikipedia page
    
    Input: the title of a wikipeida page (as a string)
    Output: a list of the internal (wikipedia) articles that are referenced on that page
    
    '''
    
    # Replace spaces with proper url notation
    item = item.replace(" ","%20")
    
    # Define the for the Wikipedia Item of Interest
    url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=cirrusdoc%7Cpageviews&list=&meta=&titles="+str(item)
    
    # Obtain object json from Wikipedia 
    data = requests.get(url)
    temp = json.loads(data.content)
    print("Recieved data for: "+item)
    # Return warning and blank dict if the page doesn't exist
    if list(temp['query']['pages'].keys())[0]=='-1':
        print("Wikipedia entry for "+item+" doesn't exisit!" )
        return({'title':"", 'description':"",'explicit_links':[], 'implied_links':[], 'avg_page_views':0})
    
    # Extract features from JSON
    for i in temp['query']['pages']:
        
        try:
            title = temp['query']['pages'][str(i)]['title']
            description = temp['query']['pages'][str(i)]['cirrusdoc'][0]['source']['opening_text']
            explicit_links = Page_Link_Extractor(temp['query']['pages'][str(i)]['cirrusdoc'][0]['source']['source_text'])
            implied_links = temp['query']['pages'][str(i)]['cirrusdoc'][0]['source']['outgoing_link']
            pageviews = temp['query']['pages'][str(i)]['pageviews']
            avg_page_views = pd.DataFrame(list(pageviews.items()), columns=['Date', 'Views'])['Views'].mean()
            
            time.sleep(1)
            return({'title':title, 'description':description,'explicit_links':explicit_links, 'implied_links':implied_links, 'avg_page_views':avg_page_views})
            
        except:
            time.sleep(1)
            print("Error reading JSON for: "+item)
            return({'title':"", 'description':"",'explicit_links':[], 'implied_links':[], 'avg_page_views':0})
            
