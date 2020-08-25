#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import datetime
import time
import matplotlib.pyplot as plt
import pathlib
from collections import ChainMap
import os
import re
import numpy as np


# In[2]:


def didMoreThanThisManySecondsElapsedSinceEndOfThatDay(singleDate,seconds):
    return (datetime.datetime.now() - (singleDate + datetime.timedelta(days=1))).total_seconds() > seconds


# In[3]:


excelFile='/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHat/vip_szotar_1.5.xlsx'


# In[4]:


def getSearchListFromTabName(tabName,pathToExcelFile=excelFile):
    pathToExcelFile=excelFile
    xl = pd.ExcelFile(pathToExcelFile)
    #dfs = {sheetname: xl.parse(sheetname, header=None).dropna().values.tolist() for sheetname in xl.sheet_names}
    dfs = {sheetname: [[alias for alias in person if type(alias) is not float]
                              for person in xl.parse(sheetname,header=None).values.tolist()]
                              for sheetname in xl.sheet_names}
    return dfs[tabName]


# In[5]:


def validalias(alias):
    return True
   # if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
   # else: return False


# In[6]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[7]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[8]:


def getDictionaries(clientSearchlist,dictname='clientdict'):
    dictionaries=[
    dictionary_class('clientdict',
               10,
               clientSearchlist)]
    return dictionaries


# In[9]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern, cutoffdate):
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(*[int(num) for num in re.findall(r'\d+', each)[:4]]) for each in csvs]
    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt >= datetime.datetime(*cutoffdate)]
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    return sorted_filtered_csvs


# In[32]:


def pathFinder(clientName,path=str(pathlib.Path().absolute())):
    preMomFile = 'live_'
    postMomFileSzokereso = '_szokereso_result.csv'
    postMomFileSzurt = '_szurt.csv'
    postMomFileErrorlog = '_ERRORLOG.txt'

    inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
    szokeresoResFilesPath =   path+'/'+clientName+'/szokeresores/'
    momentumraSzurtSzokeresesPath    = szokeresoResFilesPath + 'clientreszurt/'
    szokeresoResFilesPathAndWildcard = momentumraSzurtSzokeresesPath + preMomFile + '*' + postMomFileSzurt

    return preMomFile,postMomFileSzokereso,inputPathAndWildcard,postMomFileSzurt,szokeresoResFilesPath,szokeresoResFilesPathAndWildcard,momentumraSzurtSzokeresesPath

debugmode = False

listOfColsWeWantToOutput = ['TITLE', 'URL', 'AGEGROUP', 'OWNTIME', 'SCRAPETIME', 'TEXT', 'AUTHOR',
                            'OUTLET', 'TOP1', 'TOP2', 'TOP4', 'TOP8', 'TOP12', 'TOP24', 'TOP48',
                            'clientdict0', 'clientdict1','clientdict2', 'clientdict3',
                            'clientdict4', 'clientdict5','clientdict6', 'clientdict7',
                            'clientdict8', 'clientdict9',
                           ]


# In[33]:


def getOutputFiles(pathAndWildcard):
    outputFiles = glob.glob(pathAndWildcard)
    return outputFiles


# In[34]:


def getTodoFilesWithoutOutput(todoFiles,outputFiles):
    return [todoFile for todoFile in todoFiles
           if not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in outputFiles])]


# In[35]:


def doThisWhenNoFileIsFoundToProcess(sleepThisMuch=5*60):
    #print('No more files found to process. Sleeping '+str(sleepThisMuch)+' seconds.')
    print('Looped through all clients. Sleeping '+str(sleepThisMuch)+' seconds.')
    time.sleep(sleepThisMuch)


# In[36]:


def equivalences(df, equivalenceClasses):
    d = dict(ChainMap(*[dict.fromkeys(y,x) for x , y in equivalenceClasses.items()]))
    df = df.replace(d)
    df = df.mask(df.apply(pd.Series.duplicated,1))
    return df


# In[37]:


def prepareDirectories(sheetNames):
    path=str(pathlib.Path().absolute())+'/'
    for sheetName in sheetNames:
        for subdir in ['clientreszurt','dailyfreqs','weeklyfreqs']:
            os.makedirs(path+sheetName+'/'+'szokeresores/'+subdir, exist_ok=True)


# In[16]:


def prepareDict(excelFile=excelFile):
    
        
    xl = pd.ExcelFile(excelFile)
    sheetNames = [sheetName.strip() for sheetName in xl.sheet_names]
    dfs = {sheetname.strip():
           xl.parse(sheetname,header=None)
           for sheetname in xl.sheet_names}          
    prepareDirectories(sheetNames)
    return dfs


# In[17]:


def getEquivalenceClasses(df):
    equivalenceClasses = {row[1][0]: list(row[1]) for row in df.iterrows() for alias in row[1]}    
    return equivalenceClasses


# In[29]:


dfs=prepareDict()
clients=list(dfs.keys())


while True:
    for client in clients:
        preMomFile,        postMomFileSzokereso,        inputPathAndWildcard,        postMomFileSzurt,        szokeresoResFilesPath,        szokeresoResFilesPathAndWildcard,        momentumraSzurtSzokeresesPath = pathFinder(client)

        while True:
            todoFiles=get_files_sorted_by_date_after_a_date(inputPathAndWildcard,[2020,7,1,0])
            getOutputFiles(szokeresoResFilesPathAndWildcard)
            todoFilesWithoutOutput = getTodoFilesWithoutOutput(todoFiles=todoFiles,
                                                               outputFiles=getOutputFiles(szokeresoResFilesPathAndWildcard))
            if len(todoFilesWithoutOutput) == 0:
                break

            targetcsv=todoFilesWithoutOutput[0]

            targetdf = pd.read_csv(targetcsv)
            dictionaries=getDictionaries(clientSearchlist=getSearchListFromTabName(tabName=client))


            num_of_columns_for_each_dict={dictionary.name: dictionary.maxcolnum for dictionary in dictionaries}
            for each in num_of_columns_for_each_dict:
                for index in range(num_of_columns_for_each_dict[each]):
                    targetdf[each + str(index)]=''        


            for idictionary, dictionary in enumerate(dictionaries):
                for icell, cell in enumerate(list(targetdf['TEXT'])):
                    if type(cell) is not float:
                        if not len(matchfinder(cell,dictionary.searchlist)) > dictionary.maxcolnum and len(matchfinder(cell,dictionary.searchlist))>0:
                            for i, e in enumerate(matchfinder(cell,dictionary.searchlist)):
                                targetdf.loc[icell,dictionary.name+str(i)]=e                    

            filenamecore = targetcsv.split('/')[-1].split('.')[0]
            szokeresoResFilePathAndName=szokeresoResFilesPath+preMomFile+filenamecore+postMomFileSzokereso
            #targetdf = targetdf[~targetdf['clientdict0'].isna()]
            targetdf = targetdf[targetdf['clientdict0'].str.len()>0]
            
            classeddf = equivalences(targetdf[[col for col in targetdf.columns if 'client' in col]],getEquivalenceClasses(dfs[client]))



            classeddf.rename(columns={col:col+'clssd' for col in targetdf.columns},inplace=True)
            targetdf = targetdf.join(classeddf)

            print(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt)
            targetdf.drop(columns=[col for col in targetdf.columns if 'client' in col and 'clssd' not in col],inplace=True)
            targetdf.rename(columns={col:col.replace('clssd','') for col in targetdf.columns if 'client' in col},inplace=True)
            if not debugmode: targetdf[listOfColsWeWantToOutput].to_csv(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt,index=False)
            #targetdf[listOfColsWeWantToOutput].to_csv('probaout.csv',index=False)
         
    doThisWhenNoFileIsFoundToProcess()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




