#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[2]:


import glob
import datetime
import glob
import stanza
import pandas as pd
import time
import sys


# In[9]:


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


# In[11]:


momentum_searchlist = [[each] for each in list(kezidict)]


# In[12]:


def onlywithneighbours(ofthislist):
    try:
        filtered = [each for each in ofthislist 
                    if each+1 in ofthislist or each-1 in ofthislist]
    except TypeError:
        filtered = [each for each in ofthislist 
                    if str(int(each)+1) in ofthislist or str(int(each)-1) in ofthislist]
    return filtered


# In[13]:


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


# In[14]:


def validalias(alias):
    return True
   # if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
   # else: return False


# In[16]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[17]:


def fillextracols(whichdictionary, whichrowtofill, withthislist, unlessitslongerthanthis):
    if not len(withthislist) > unlessitslongerthanthis and len(withthislist)>0:
        for i, e in enumerate(withthislist):
            targetdf.loc[whichrowtofill,whichdictionary+str(i)]=e


# In[18]:


def prepare_extra_columns(num_of_columns_for_each_dict):
    for each in num_of_columns_for_each_dict:
        for index in range(num_of_columns_for_each_dict[each]):
            targetdf[each + str(index)]=''


# In[19]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[20]:


dictionaries=[
dictionary_class('momentumdict',
           10,
           momentum_searchlist)]


# In[21]:


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


# In[ ]:


debugmode = False

preMomFile = 'live_updated3_dict_onlymomentum_'
postMomFileSzokereso = '_szokereso_result.csv'
postMomFileSzurt = '_dfUnifiedNanFilteredOnlySomeColsUpdated3.csv'
postMomFileErrorlog = '_ERRORLOG.txt'

inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
szokeresoResFilesPath =   '/mnt/volume/jupyter/szokereso/cron/szokeresores/'
szokeresoResFilesPathAndWildcard = szokeresoResFilesPath + preMomFile + '*' + postMomFileSzokereso
momentumraSzurtSzokeresesPath    = szokeresoResFilesPath + 'momentumraszurt/'


listOfColsWeWantToOutput = ['DOC_ID','TITLE','SCRAPETIME','TEXT','momentumdict0', 'momentumdict1',
                            'momentumdict2', 'momentumdict3', 'momentumdict4', 'momentumdict5',
                            'momentumdict6', 'momentumdict7', 'momentumdict8', 'momentumdict9']


# In[45]:


def getOutputFiles(pathAndWildcard=szokeresoResFilesPathAndWildcard):
    outputFiles = glob.glob(pathAndWildcard)
    return outputFiles


# In[46]:


def getTodoFilesWithoutOutput(todoFiles,outputFiles=getOutputFiles()):
    return [todoFile for todoFile in todoFiles
           if not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in getOutputFiles()])]


# In[47]:


def doThisWhenNoFileIsFoundToProcess(sleepThisMuch=5*60):
    print('No more files found to process. Sleeping '+str(sleepThisMuch)+' seconds.')
    time.sleep(sleepThisMuch)


# In[ ]:


while True:

    todoFiles=get_files_sorted_by_date_after_a_date(inputPathAndWildcard,[2020,7,1,0])
    todoFilesWithoutOutput = getTodoFilesWithoutOutput(todoFiles)
    
    if len(todoFilesWithoutOutput) == 0:
        doThisWhenNoFileIsFoundToProcess()
        continue
        
    print('processing: '+todoFilesWithoutOutput[0])    

    targetcsv=todoFilesWithoutOutput[0]
    try:
        targetdf = pd.read_csv(targetcsv)
        prepare_extra_columns({dictionary.name: dictionary.maxcolnum for dictionary in dictionaries})
        for idictionary, dictionary in enumerate(dictionaries):
            for icell, cell in enumerate(list(targetdf['TEXT'])):
                if type(cell) is not float:
                    if dictionary.searchlist is not None:
                        fillextracols(dictionary.name,icell,matchfinder(cell,dictionary.searchlist),dictionary.maxcolnum)
                    if dictionary.searchlist is None:
                        fillextracols(dictionary.name,icell,stanzanamesearch(cell),dictionary.maxcolnum)
        
        filenamecore = targetcsv.split('/')[-1].split('.')[0]
        szokeresoResFilePathAndName=szokeresoResFilesPath+preMomFile+filenamecore+postMomFileSzokereso
        
        if not debugmode: targetdf.to_csv(szokeresoResFilePathAndName)

        df = pd.read_csv(szokeresoResFilePathAndName)
        df = df[~df['momentumdict0'].isna()]
        df[listOfColsWeWantToOutput].to_csv(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt)

    except KeyboardInterrupt:
        break
    except:
        the_type, the_value, the_traceback = sys.exc_info()
        outlist = [the_type, the_value, targetcsv, dictionary.name, icell]
        if not debugmode:
            with open(szokeresoResFilePathAndName+postMomFileErrorlog, 'w') as f:
                for item in outlist:
                    f.write("%s\n" % item)

