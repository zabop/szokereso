#!/usr/bin/env python
# coding: utf-8

# In[66]:


import glob
import datetime
import glob
import stanza
import pandas as pd
import time
import sys


# In[67]:


def filetime(file):
    year=file.split('/')[-1][5:9]
    month=file.split('/')[-1][10:12]
    day=file.split('/')[-1][13:15]
    hour=file.split('/')[-1][16:18]
    return [int(each) for each in [year, month, day, hour]]


# In[68]:


stanza.download('hu')
nlp = stanza.Pipeline('hu')


# In[69]:


def onlywithneighbours(ofthislist):
    try:
        filtered = [each for each in ofthislist 
                    if each+1 in ofthislist or each-1 in ofthislist]
    except TypeError:
        filtered = [each for each in ofthislist 
                    if str(int(each)+1) in ofthislist or str(int(each)-1) in ofthislist]
    return filtered


# In[70]:


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


# In[71]:


def stanzanamesearch(text):

    try: doc = nlp(text)
    except IndexError: return []
    
    propns_and_their_positions_dictlist = [{
    #word.id:word.lemma
    word.id:word.text
    for word in sentence.words if word.upos == 'PROPN'}
    for sentence in doc.sentences]

    propns_with_at_least_one_propn_neighbour = [[
    eachdict[eachkey]
    for eachkey in sorted(onlywithneighbours(list(eachdict.keys())))]
    for eachdict in propns_and_their_positions_dictlist]

    propn_ids_with_at_least_one_propn_neighbour = [[
    int(eachkey)
    for eachkey in sorted(onlywithneighbours(list(eachdict.keys())))]
    for eachdict in propns_and_their_positions_dictlist]

    propn_id_sequences_with_at_least_one_propn_neighbour=[
    split_into_numerical_sequences(eachsublist)
    for eachsublist in propn_ids_with_at_least_one_propn_neighbour]

    res=[]
    for sentenceindex, eachsentence in enumerate(propn_id_sequences_with_at_least_one_propn_neighbour):
        for sequenceindex, eachsequence in enumerate(eachsentence):
            name=[]
            for wordindex, eachword in enumerate(eachsequence):
                name.append(propns_and_their_positions_dictlist[sentenceindex][str(eachword)])
            name=' '.join(name)
            res.append(name)

    return list(set(res))


# In[72]:


def validalias(alias):
    if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
    else: return False


# In[73]:


def matchfinder(text,searchforthese):
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias) and alias.lower() in str(text).lower()]
    return matches


# In[74]:


def fillextracols(whichdictionary, whichrowtofill, withthislist, unlessitslongerthanthis):
    if not len(withthislist) > unlessitslongerthanthis and len(withthislist)>0:
        for i, e in enumerate(withthislist):
            targetdf.loc[whichrowtofill,whichdictionary+str(i)]=e


# In[75]:


def prepare_extra_columns(num_of_columns_for_each_dict):
    for each in num_of_columns_for_each_dict:
        for index in range(num_of_columns_for_each_dict[each]):
            targetdf[each + str(index)]=''


# In[76]:


class dictionary_class:
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[29]:


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


# In[92]:


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


# In[93]:


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


# In[94]:


debugmode = False
wildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'

todofiles=get_files_sorted_by_date_after_a_date('/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv',
                                               [2020,7,14,0])
while len(todofiles) != 0:
    print('processing: '+todofiles[0])    
    
    targetcsv=todofiles[0]
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
                            if icell%10==0: print(icell)
                            if dictionary.searchlist is not None:
                                fillextracols(dictionary.name,icell,matchfinder(cell,dictionary.searchlist),dictionary.maxcolnum)
                                print('hw')
                            if dictionary.searchlist is None:
                                fillextracols(dictionary.name,icell,stanzanamesearch(cell),dictionary.maxcolnum)
        end_time = time.time()
        print("--- %s seconds ---" % (time.time() - start_time))
        if not debugmode: targetdf.to_csv('/mnt/volume/jupyter/szokereso/resultfiles/'+targetcsv.split('/')[-1].split('.')[0]+'_szokereso_result.csv')
        print(targetcsv)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        break
    except:
        the_type, the_value, the_traceback = sys.exc_info()
        outlist = [the_type, the_value, targetcsv, dictionary.name, icell]
        if not debugmode:
            with open('/mnt/volume/jupyter/szokereso/resultfiles/'+targetcsv.split('/')[-1].split('.')[0]+'_ERRORLOG.txt', 'w') as f:
                for item in outlist:
                    f.write("%s\n" % item)
                
    todofiles=get_files_sorted_by_date_after_a_date('/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv',
                                                     filetime(todofiles[0])[:3]+[filetime(todofiles[0])[-1]+1]) # hour increased by 1


# In[ ]:




