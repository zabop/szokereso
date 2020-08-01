#!/usr/bin/env python
# coding: utf-8

# In[4]:


import glob
import datetime
import glob
import stanza
import pandas as pd
import time
import sys


# In[29]:


def getOutputFiles(path='resultfiles/onlymomentum/kulonmappa/live_updated3_dict_onlymomentum_*2020-07*_dfUnifiedNanFilteredOnlySomeColsUpdated3.csv'):
    outputFiles = glob.glob(path)
    return outputFiles


# In[6]:


kezidict = set([
'Fekete-Győr András',
'Borbélyné Bárdi Zsuzsanna',
'Hajnal Miklós',
'Körömi Attila',
'Mándi László',
'Orosz Anna',
'Tóth Endre',
'Cseh Katalin',
'Donáth Anna Júlia',
'Soproni Tamás',
'Déri Tibor',
'Orosz Anna',
'Nyirati Klára',
'Pikó András',
'Balogh Csaba',
'Kerpel-Fronius Gábor',
'Momentum',
'momentum',
'Fekete-Győr'
'Fekete Győr',
'Donáth Anna'
'Donáth',
'Nyirati',
'Pikó',
'Kerpel-Fronius',
'Mándi',
'Körömi',
'Kádár Barnabás',
'Hadházy',
'Hadházy Ákos'
'Szél Bernadett',
])


# In[7]:


momentum_searchlist = [[each] for each in list(kezidict)]


# In[8]:


def filetime(file):
    year=file.split('/')[-1][5:9]
    month=file.split('/')[-1][10:12]
    day=file.split('/')[-1][13:15]
    hour=file.split('/')[-1][16:18]
    return [int(each) for each in [year, month, day, hour]]


# In[9]:


def onlywithneighbours(ofthislist):
    try:
        filtered = [each for each in ofthislist 
                    if each+1 in ofthislist or each-1 in ofthislist]
    except TypeError:
        filtered = [each for each in ofthislist 
                    if str(int(each)+1) in ofthislist or str(int(each)-1) in ofthislist]
    return filtered


# In[10]:


def split_into_numerical_sequences(inlist):

    inlist=sorted(inlist)

    breakindeces=[i for i,j in enumerate(inlist)
                    if (j+1 not in inlist and j in inlist)]

    sublists=[]
    for index, each in enumerate(breakindeces):
        if index==0:
            sublists.append([x for x in inlist
                               if x<=inlist[each]])
        if index!=0:
            sublists.append([x for x in inlist
                               if x<=inlist[each] and x>inlist[breakindeces[index-1]]])

    return sublists


# In[11]:


def validalias(alias):
    return True
   # if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
   # else: return False


# In[12]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[13]:


def fillextracols(whichdictionary, whichrowtofill, withthislist, unlessitslongerthanthis):
    if not len(withthislist) > unlessitslongerthanthis and len(withthislist)>0:
        for i, e in enumerate(withthislist):
            targetdf.loc[whichrowtofill,whichdictionary+str(i)]=e


# In[14]:


def prepare_extra_columns(num_of_columns_for_each_dict):
    for each in num_of_columns_for_each_dict:
        for index in range(num_of_columns_for_each_dict[each]):
            targetdf[each + str(index)]=''


# In[15]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[16]:


dictionaries=[
dictionary_class('momentumdict',
           10,
           momentum_searchlist)]


# In[17]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern,cutoffdate):
    
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(int(each.split('/')[-1][5:9]),
                             int(each.split('/')[-1][10:12]),
                             int(each.split('/')[-1][13:15]),
                             int(each.split('/')[-1][16:18]),
                             int(each.split('/')[-1][19:21]),
                             int(each.split('/')[-1][22:24])) for each in csvs]

    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt > datetime.datetime(*cutoffdate)]
    
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    
    return sorted_filtered_csvs


# In[28]:


debugmode = False
wildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'

while True:

    todofiles=get_files_sorted_by_date_after_a_date('/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv',
                                                   [2020,7,1,0])


    todofilesWithoutOutput = [todofile
                             for itodofile, todofile in enumerate(todofiles)
                             if not any(
                             [todofile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in getOutputFiles()])]

    print('###')
    print(len(getOutputFiles()))
    print('###')
    
    if len(todofilesWithoutOutput) == 0:
        
        print('No more files found to process. Sleeping 5 mins')
        time.sleep(5*60)
        continue

#    while len(todofilesWithoutOutput) != 0:
    print('processing: '+todofilesWithoutOutput[0])    

    targetcsv=todofilesWithoutOutput[0]
    try:
        targetdf = pd.read_csv(targetcsv)

        prepare_extra_columns({dictionary.name: dictionary.maxcolnum for dictionary in dictionaries})

        cells = list(targetdf['TEXT'])

        start_time = time.time()
        for idictionary, dictionary in enumerate(dictionaries):
            if idictionary==7 or not debugmode:
            #if dictionary.name == 'instit_dict':
                for icell, cell in enumerate(cells):
                    if type(cell) is not float:
                        if icell < 10 or not debugmode:
                            if icell%1000==0: print(icell)
                            if dictionary.searchlist is not None:
                                fillextracols(dictionary.name,icell,matchfinder(cell,dictionary.searchlist),dictionary.maxcolnum)
                                #print('hw')
                            if dictionary.searchlist is None:
                                fillextracols(dictionary.name,icell,stanzanamesearch(cell),dictionary.maxcolnum)
        end_time = time.time()
        print("--- %s seconds ---" % (time.time() - start_time))
        if not debugmode: targetdf.to_csv('/mnt/volume/jupyter/szokereso/resultfiles/onlymomentum/kulonmappa/live_updated3_dict_onlymomentum_'+targetcsv.split('/')[-1].split('.')[0]+'_szokereso_result.csv')
        print(targetcsv)

        df = pd.read_csv('/mnt/volume/jupyter/szokereso/resultfiles/onlymomentum/kulonmappa/live_updated3_dict_onlymomentum_'+targetcsv.split('/')[-1].split('.')[0]+'_szokereso_result.csv')
        df = df[~df['momentumdict0'].isna()]
        df[['DOC_ID','TITLE','SCRAPETIME','TEXT','momentumdict0', 'momentumdict1',
            'momentumdict2', 'momentumdict3', 'momentumdict4', 'momentumdict5',
            'momentumdict6', 'momentumdict7', 'momentumdict8', 'momentumdict9']].to_csv('/mnt/volume/jupyter/szokereso/resultfiles/onlymomentum/kulonmappa/live_updated3_dict_onlymomentum_'+targetcsv.split('/')[-1].split('.')[0]+'_dfUnifiedNanFilteredOnlySomeColsUpdated3.csv')

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        break
    except:
        the_type, the_value, the_traceback = sys.exc_info()
        outlist = [the_type, the_value, targetcsv, dictionary.name, icell]
        if not debugmode:
            with open('/mnt/volume/jupyter/szokereso/resultfiles/onlymomentum/kulonmappa/live_updated3_dict_onlymomentum_'+targetcsv.split('/')[-1].split('.')[0]+'_ERRORLOG.txt', 'w') as f:
                for item in outlist:
                    f.write("%s\n" % item)

    #todofiles=get_files_sorted_by_date_after_a_date('/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv',
    #                                                 filetime(todofiles[0])[:3]+[filetime(todofiles[0])[-1]+1]) # hour increased by 1


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




