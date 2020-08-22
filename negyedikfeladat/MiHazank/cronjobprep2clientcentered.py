#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import datetime
import glob
import stanza
import pandas as pd
import time
import sys


# In[2]:


clientName = 'MiHazánk'
clientNameEkezetekNelkul = 'MiHazank'


# In[3]:


def getSearchListFromTabName(pathToExcelFile,tabName):
    xl = pd.ExcelFile('/mnt/volume/jupyter/szokereso/vip_szotar_1.1.xlsx')
    dfs = {sheetname:
           [[each] for each in xl.parse(sheetname,header=None)[0]]
                   for sheetname in xl.sheet_names
                   if 'Momentum' not in sheetname}
    return dfs[tabName]


# In[4]:


clientSearchlist = getSearchListFromTabName('/mnt/volume/jupyter/szokereso/vip_szotar_1.1.xlsx',clientName)


# In[5]:


def onlywithneighbours(ofthislist):
    try:
        filtered = [each for each in ofthislist 
                    if each+1 in ofthislist or each-1 in ofthislist]
    except TypeError:
        filtered = [each for each in ofthislist 
                    if str(int(each)+1) in ofthislist or str(int(each)-1) in ofthislist]
    return filtered


# In[6]:


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


# In[7]:


def validalias(alias):
    return True
   # if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
   # else: return False


# In[8]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[9]:


def fillextracols(whichdictionary, whichrowtofill, withthislist, unlessitslongerthanthis):
    if not len(withthislist) > unlessitslongerthanthis and len(withthislist)>0:
        for i, e in enumerate(withthislist):
            targetdf.loc[whichrowtofill,whichdictionary+str(i)]=e


# In[10]:


def prepare_extra_columns(num_of_columns_for_each_dict):
    for each in num_of_columns_for_each_dict:
        for index in range(num_of_columns_for_each_dict[each]):
            targetdf[each + str(index)]=''


# In[11]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[12]:


dictionaries=[
dictionary_class('clientdict',
           10,
           clientSearchlist)]


# In[13]:


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


# In[14]:


debugmode = False

preMomFile = 'live_updated3_dict_onlymomentum_'
preMomFile = 'live_updated3_dict_only_1client_'
postMomFileSzokereso = '_szokereso_result.csv'
postMomFileSzurt = '_dfUnifiedNanFilteredOnlySomeColsUpdated3.csv'
postMomFileErrorlog = '_ERRORLOG.txt'

inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
szokeresoResFilesPath =   '/mnt/volume/jupyter/szokereso/negyedikfeladat/'+clientNameEkezetekNelkul+'/szokeresores/'
szokeresoResFilesPathAndWildcard = szokeresoResFilesPath + preMomFile + '*' + postMomFileSzokereso
momentumraSzurtSzokeresesPath    = szokeresoResFilesPath + 'clientreszurt/'


listOfColsWeWantToOutput = ['DOC_ID','TITLE','SCRAPETIME','TEXT','OUTLET','clientdict0', 'clientdict1',
                            'clientdict2', 'clientdict3', 'clientdict4', 'clientdict5',
                            'clientdict6', 'clientdict7', 'clientdict8', 'clientdict9']


# In[15]:


def getOutputFiles(pathAndWildcard=szokeresoResFilesPathAndWildcard):
    outputFiles = glob.glob(pathAndWildcard)
    return outputFiles


def getTodoFilesWithoutOutput(todoFiles,outputFiles=getOutputFiles()):
    return [todoFile for todoFile in todoFiles
           if not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in getOutputFiles()])]




def doThisWhenNoFileIsFoundToProcess(sleepThisMuch=5*60):
    print('No more files found to process. Sleeping '+str(sleepThisMuch)+' seconds.')
    time.sleep(sleepThisMuch)


# In[18]:


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
        
        if not debugmode:
            targetdf.to_csv(szokeresoResFilePathAndName)
        
        df = pd.read_csv(szokeresoResFilePathAndName)
        df = df[~df['clientdict0'].isna()]
        
      #  classeddf = equivalences(df[[col for col in df.columns if 'momentum' in col]],equivalenceClasses)
      #  classeddf.rename(columns={col:col+'clssd' for col in df.columns},inplace=True)
      #  df = df.join(classeddf)
        
        if not debugmode: df[listOfColsWeWantToOutput].to_csv(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt)

    except KeyboardInterrupt:
        break
   # except:
   #     print('exception occured')
   #     the_type, the_value, the_traceback = sys.exc_info()
   #     outlist = [the_type, the_value, targetcsv, dictionary.name, icell]
   #     if not debugmode:
   #         with open(szokeresoResFilePathAndName+postMomFileErrorlog, 'w') as f:
   #             for item in outlist:
   #                 f.write("%s\n" % item)


# In[ ]:




