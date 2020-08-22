#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import datetime
import pandas as pd
import time
import pathlib
import re


# In[2]:


def validalias(alias):
    if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
    else: return False


# In[3]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[4]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


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
dictionary_class('person_data',
           10,
           searchlist_maker('/mnt/volume/jupyter/szokereso/person_data-1592394309231_utf8.csv',alias_separator='|')),
dictionary_class('wikilist',
           5,
           searchlist_maker('/mnt/volume/jupyter/szokereso/A_negyedik_Orbán-kormany_allamtitkarainak_listaja.csv')),
dictionary_class('stanza',
           10),
dictionary_class('settlement_list',
           5,
           searchlist_maker('/mnt/volume/jupyter/szokereso/List of Settlements_m2.xlsx', excelfile=True,headerwechoose='settlement_name'),
           geo=True),
dictionary_class('szotar_2.1',
           10,
           searchlist_maker('/mnt/volume/jupyter/szokereso/szotar_2.1.xlsx',multisheet=True)),
dictionary_class('instit_dict',
            10,
            searchlist_maker('/mnt/volume/jupyter/szokereso/instit_dict_2.1_updated_headers.xlsx',
                             multisheet=True,
                             columnsfiltered=True)),
dictionary_class('geo2dict',
                10,
                searchlist_maker('/mnt/volume/jupyter/szokereso/geo2.csv',
                             multisheet=False,
                             columnsfiltered=False,
                             alias_separator='|')),
dictionary_class('corporate2dict',
                 10,
                 searchlist_maker('/mnt/volume/jupyter/szokereso/corporate2.csv',
                             multisheet=False,
                             columnsfiltered=False,
                             alias_separator='|'))]


# In[7]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern, cutoffdate):
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(*[int(num) for num in re.findall(r'\d+', each)[:4]]) for each in csvs]
    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt >= datetime.datetime(*cutoffdate)]
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    return sorted_filtered_csvs


# In[ ]:


debugmode = False
inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
todoFiles=get_files_sorted_by_date_after_a_date(inputPathAndWildcard,[2020,7,1,0])
while True:
    targetcsv=todoFiles[0]
    
    targetdf = pd.read_csv(targetcsv)
    
    num_of_columns_for_each_dict={dictionary.name: dictionary.maxcolnum for dictionary in dictionaries}
    for each in num_of_columns_for_each_dict:
        for index in range(num_of_columns_for_each_dict[each]):
            targetdf[each + str(index)]=''
   
    cells = list(targetdf['TEXT'])
    
    for idictionary, dictionary in enumerate(dictionaries):
        print(dictionary)
        for icell, cell in enumerate(list(targetdf['TEXT'])):
            if icell%100 == 0: print(icell)
            if type(cell) is not float            and not len(matchfinder(cell,dictionary.searchlist)) > dictionary.maxcolnum            and len(matchfinder(cell,dictionary.searchlist))>0:
                for i, e in enumerate(matchfinder(cell,dictionary.searchlist)):
                    targetdf.loc[icell,dictionary.name+str(i)]=e  
    
    targetdf.to_csv('resultfiles/nagyszokereso_'+targetcsv.split('/')[-1])
    
    todofiles=get_files_sorted_by_date_after_a_date('/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv',
                filetime(todofiles[0])[:3]+[filetime(todofiles[0])[-1]+1]) # hour increased by 1


# In[ ]:





# In[ ]:




