#!/usr/bin/env python
# coding: utf-8

# In[3]:


import glob
import datetime
import pandas as pd
import time
import pathlib
import re


# In[4]:


import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHet')
import szokereso_functions as sf


# In[5]:


def searchlist_maker(csv,excelfile=False,multisheet=False,columnsfiltered=False, headerwechoose='name_list',**kwargs):
    
    if not multisheet:
        if excelfile: persondatadict = pd.read_excel(csv)

        else:
            persondatadict = pd.read_csv(csv)

        if 'alias_separator' in kwargs:
            persondata_searchlist = [[eachalias.strip()
                                    for eachalias in eachperson.split(kwargs['alias_separator'])]
                                    for eachperson in persondatadict[headerwechoose]
                                    if type(eachperson) != float]
        else:
            persondata_searchlist = [[each]
                                    for each in persondatadict[headerwechoose]]

    if multisheet:
        
        if not columnsfiltered:

            xls=pd.ExcelFile(csv)
            dfs=[pd.read_excel(xls,sheet) for i, sheet in enumerate(xls.sheet_names)]
            persondata_searchlist=[[name] for df in dfs for name in df['name_list'] if type(name) is not float]

        if columnsfiltered:
            
            unifieddf=pd.concat([pd.read_excel(csv, sheetname)[column]
                        for sheetname in pd.ExcelFile(csv).sheet_names
                        for column in pd.read_excel(csv, sheetname)
                        if 'LOOKFOR' in column]).dropna().drop_duplicates()
            
            persondata_searchlist = [[each] for each in unifieddf]
            
    return persondata_searchlist


# In[6]:


dictionaries=[
sf.dictionary_class('person_data',
           10,
           searchlist_maker('/mnt/volume/jupyter/szokereso/person_data-1592394309231_utf8.csv',alias_separator='|')),
sf.dictionary_class('wikilist',
           5,
           searchlist_maker('/mnt/volume/jupyter/szokereso/A_negyedik_Orbán-kormany_allamtitkarainak_listaja.csv')),
#dictionary_class('stanza',
#           10),
sf.dictionary_class('settlement_list',
           5,
           searchlist_maker('/mnt/volume/jupyter/szokereso/List of Settlements_m2.xlsx', excelfile=True,headerwechoose='settlement_name'),
           geo=True),
sf.dictionary_class('szotar_2.1',
           10,
           searchlist_maker('/mnt/volume/jupyter/szokereso/szotar_2.1.xlsx',multisheet=True)),
sf.dictionary_class('instit_dict',
            10,
            searchlist_maker('/mnt/volume/jupyter/szokereso/instit_dict_2.1_updated_headers.xlsx',
                             multisheet=True,
                             columnsfiltered=True)),
sf.dictionary_class('geo2dict',
                10,
                searchlist_maker('/mnt/volume/jupyter/szokereso/geo2.csv',
                             multisheet=False,
                             columnsfiltered=False,
                             alias_separator='|')),
sf.dictionary_class('corporate2dict',
                 10,
                 searchlist_maker('/mnt/volume/jupyter/szokereso/corporate2.csv',
                             multisheet=False,
                             columnsfiltered=False,
                             alias_separator='|'))]


# In[7]:


inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
debugmode=False

# In[9]:

while True:
    while True:
        todoFiles=sf.get_files_sorted_by_date_after_a_date(inputPathAndWildcard,[2020,7,15,0])
        szokeresoResFilesPathAndWildcard='/mnt/volume/jupyter/szokereso/ujfajlnezo7/resultfiles/nagyszokereso_data_*'
        todoFilesWithoutOutput = sf.getTodoFilesWithoutOutput(
                                    todoFiles=todoFiles,
                                    outputFiles=sf.getOutputFiles(szokeresoResFilesPathAndWildcard))
        if len(todoFilesWithoutOutput) == 0: break
        
        targetcsv = todoFilesWithoutOutput[0]
        targetdf = pd.read_csv(targetcsv)
        print(targetcsv)

        num_of_columns_for_each_dict={dictionary.name: dictionary.maxcolnum for dictionary in dictionaries}
        for each in num_of_columns_for_each_dict:
            for index in range(num_of_columns_for_each_dict[each]):
                #See: https://stackoverflow.com/a/29517089/8565438
                targetdf[each + str(index)]=''
                
        for idictionary, dictionary in enumerate(dictionaries):
            print(dictionary.name)
            print(idictionary)
            for icell, cell in enumerate(list(targetdf['TEXT'])):
                if icell%1000 == 0: print(icell)
                sf_matchfinder=sf.matchfinder(cell,dictionary.searchlist, strictfiltering=True)
                if type(cell) is not float and not len(sf_matchfinder) > dictionary.maxcolnum and len(sf_matchfinder)>0:
                    for i, e in enumerate(sf_matchfinder):
                        targetdf.loc[icell,dictionary.name+str(i)]=e  
           
        if not debugmode: targetdf.to_csv('resultfiles/nagyszokereso_'+targetcsv.split('/')[-1])
            
    sf.doThisWhenNoFileIsFoundToProcess(5*60)


# In[ ]:





# In[ ]:




