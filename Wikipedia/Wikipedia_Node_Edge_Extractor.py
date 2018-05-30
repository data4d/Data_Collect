# -*- coding: utf-8 -*-
"""
Created on Sat May 19 17:14:29 2018

@author: GTayl
"""
################################## Set-up ##########################################

# Import the required packages
import pandas as pd
import time
import os
from pandas import ExcelWriter
from pandas import ExcelFile

# Change the working directory
os.chdir("C:\\Users\\GTayl\\Desktop\\Finance Modeling\\Wikipedia")
cwd = os.getcwd()
from Wikipedia_Page_Features import Get_Wiki_Page_Data 

################################## Data-Prep ##########################################

# Read in Seed List
seed_file = "Machine_Learning_Seed_List.xlsx"
seed_import = pd.read_excel(cwd+"\\Seeds\\"+seed_file,names=['Page','Tag'],header=None)

# Dedoop Seeds and Define Tags

# Obtain deduped seed list
seed_list = pd.DataFrame(seed_import['Page']).drop_duplicates()

def seed_tag_collector(seed_import, seed):
    
    # Subset Dataframe for Seed Entry only
    temp = seed_import[seed_import['Page']==seed]
    
    # Get a list of all the tags that apply to that seed and convert to a Kumu compliant text string
    tag_list = list(temp['Tag'])
    tag_string = ""
    for tag in tag_list:
        tag_string = tag_string+str(tag)+"|"
    tag_string = tag_string[:-1]
    return(tag_string)

# Generate Seed List with Coresponding Tags
seed_list['Tags'] = ""
seed_list['Tags'] = seed_list.apply(lambda row: seed_tag_collector(seed_import, row['Page']),axis=1)

# test = seed_list.head(100)
# seed_list = test

################################## Wikipedia API Call ##########################################

# Initalize Master Lists
Master_Node_List = pd.DataFrame(columns=['Label','Tags','Description','Average_pg_views'])
Master_Direct_Edge_List = pd.DataFrame(columns=['To','From','Strength','Tag'])
Master_Implied_Edge_List = pd.DataFrame(columns=['To','From','Strength','Tag'])

# API Call for Seed Set
for index, row in seed_list.iterrows():
    print("Collecting data for: "+str(row['Page']))
    page = Get_Wiki_Page_Data(str(row['Page']))

    # Append node features
    Master_Node_List = Master_Node_List.append({'Label':page['title'], 'Tags':row['Tags'],'Description':page['description'], 'Average_pg_views':page['avg_page_views']}, ignore_index=True)
    
    # Append edge features
    for e in page['explicit_links']:
        Master_Direct_Edge_List = Master_Direct_Edge_List.append({"To":str(e), "From":page['title'], "Strength":1, "Tag":"Direct"}, ignore_index=True)
    
    for e in page['implied_links']:
        Master_Implied_Edge_List = Master_Implied_Edge_List.append({"To":str(e), "From":page['title'], "Strength":1, "Tag":"Implied"}, ignore_index=True)
    
    time.sleep(1.5)
 
# Cleaning Direct Edge List
# Cleaned_Edges = Master_Edge_List[Master_Edge_List['Tag']=='Direct']

################################## Wikipedia API Call - Secondary Links ##########################################
    
Cleaned_Edges = pd.DataFrame(Master_Direct_Edge_List['To']).drop_duplicates()
#Cleaned_Edges = Cleaned_Edges.rename(index=str, columns={'To':'Label'})
#s1 = pd.merge(Master_Node_List, Cleaned_Edges, how='outer', on=['Label'])

# Unique Nodes that were not in the original seed set
Unique_New_Nodes = list(set(Cleaned_Edges.To).difference(Master_Node_List.Label))

Secondary_Node_List = pd.DataFrame(columns=['Label','Tags','Description','Average_pg_views'])
Secondary_Direct_Edge_List = pd.DataFrame(columns=['To','From','Strength','Tag'])
Secondary_Implied_Edge_List = pd.DataFrame(columns=['To','From','Strength','Tag'])

# API Call for Secondary Set
for Page in Unique_New_Nodes:
    print("Collecting data for: "+str(Page))
    page = Get_Wiki_Page_Data(str(Page))

    # Append node features
    Secondary_Node_List = Secondary_Node_List.append({'Label':page['title'], 'Tags':"",'Description':page['description'], 'Average_pg_views':page['avg_page_views']}, ignore_index=True)

    # Append edge features
    for e in page['explicit_links']:
        Secondary_Direct_Edge_List = Secondary_Direct_Edge_List.append({"To":str(e), "From":page['title'], "Strength":1, "Tag":"Direct"}, ignore_index=True)
    
    #for e in page['implied_links']:
        #Secondary_Implied_Edge_List = Secondary_Implied_Edge_List.append({"To":str(e), "From":page['title'], "Strength":1, "Tag":"Implied"}, ignore_index=True)
    
    time.sleep(0.5)

################################## Exporing Data ##########################################
    
# Export Edges and Nodes Lists
Master_Node_List.to_excel(cwd+"\\Seeds\\"+'ML_Node_List_Master_Final.xlsx',index=False)
Master_Direct_Edge_List.to_excel(cwd+"\\Seeds\\"+'ML_Direct_Edge_List_Master_Final.xlsx',index=False)  
Secondary_Node_List.to_excel(cwd+"\\Seeds\\"+'ML_Node_List_Secondary_Final.xlsx',index=False)
Secondary_Direct_Edge_List.to_excel(cwd+"\\Seeds\\"+'ML_Direct_Edge_List_Secondary_Final.xlsx',index=False)

################################## Exploring Data ##########################################

# EDA of Edges
# Master Edge Counts
Master_Edge_Counts = pd.DataFrame(Master_Direct_Edge_List['To'])
Master_Edge_Counts = Master_Edge_Counts['To'].value_counts()

# Secondary Edge Counts (only for nodes in the Master or Secondary Lists)
Complete_Node_List = Unique_New_Nodes + list(Master_Node_List.Label)
Subset_Edges_List = Secondary_Direct_Edge_List[Secondary_Direct_Edge_List['To'].isin(Complete_Node_List)]


Joint_Edge_Counts = pd.DataFrame(Master_Direct_Edge_List['To'])
Joint_Edge_Counts = Joint_Edge_Counts.append(Subset_Edges_List, ignore_index=True)
Joint_Edge_Counts = Joint_Edge_Counts['To'].value_counts()

Joint_Edge_Counts.to_excel(cwd+"\\Seeds\\"+'ML_Joint_Edge_Counts_Final.xlsx',index=False)

