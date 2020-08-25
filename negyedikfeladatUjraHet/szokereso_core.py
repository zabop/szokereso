#!/usr/bin/env python
# coding: utf-8

# In[4]:


import szokereso_functions as sf
import pandas as pd
import pathlib


# In[7]:


excelFile='/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHat/vip_szotar_1.5.xlsx'

listOfColsWeWantToOutput = ['TITLE', 'URL', 'AGEGROUP', 'OWNTIME', 'SCRAPETIME', 'TEXT', 'AUTHOR',
                            'OUTLET', 'TOP1', 'TOP2', 'TOP4', 'TOP8', 'TOP12', 'TOP24', 'TOP48',
                            'clientdict0', 'clientdict1','clientdict2', 'clientdict3',
                            'clientdict4', 'clientdict5','clientdict6', 'clientdict7',
                            'clientdict8', 'clientdict9']

debugmode=False
path=str(pathlib.Path().absolute())


# In[8]:


dfs = sf.prepareDirectoryTreeAndReturnDfs(excelFile,path)
clients=list(dfs.keys())

while True:
    for client in clients:
        
        preMomFile,        postMomFileSzokereso,        inputPathAndWildcard,        postMomFileSzurt,        szokeresoResFilesPath,        szokeresoResFilesPathAndWildcard,        momentumraSzurtSzokeresesPath = sf.pathFinder(client,path=path)
        
        while True:
            todoFiles = sf.get_files_sorted_by_date_after_a_date(inputPathAndWildcard,[2020,7,1,0])
            todoFilesWithoutOutput = sf.getTodoFilesWithoutOutput(
                                        todoFiles=todoFiles,
                                        outputFiles=sf.getOutputFiles(szokeresoResFilesPathAndWildcard))
            if len(todoFilesWithoutOutput) == 0: break
            targetcsv=todoFilesWithoutOutput[0]
            targetdf = pd.read_csv(targetcsv)
            #dictionaries=getDictionaries(clientSearchlist=getSearchListFromTabName(tabName=client))

            dictionary = sf.dictionary_class('clientdict',10,sf.getSearchListFromTabName(tabName=client,excelFile=excelFile))
            
            #num_of_columns_for_each_dict={dictionary.name: dictionary.maxcolnum for dictionary in dictionaries}
            num_of_columns_for_each_dict={dictionary.name: dictionary.maxcolnum}
            for each in num_of_columns_for_each_dict:
                for index in range(num_of_columns_for_each_dict[each]):
                    targetdf[each + str(index)]=''
                    
            for icell, cell in enumerate(list(targetdf['TEXT'])):
                if type(cell) is not float:
                    sf_matchfinder=sf.matchfinder(cell,dictionary.searchlist)
                    if not len(sf_matchfinder) > dictionary.maxcolnum and len(sf_matchfinder)>0:
                        for i, e in enumerate(sf_matchfinder):
                            targetdf.loc[icell,dictionary.name+str(i)]=e
                                            
            filenamecore = targetcsv.split('/')[-1].split('.')[0]
            szokeresoResFilePathAndName=szokeresoResFilesPath+preMomFile+filenamecore+postMomFileSzokereso
            targetdf = targetdf[targetdf['clientdict0'].str.len()>0]

            classeddf = sf.equivalences(
                targetdf[[col for col in targetdf.columns if 'client' in col]],sf.getEquivalenceClasses(dfs[client]))

            classeddf.rename(columns={col:col+'clssd' for col in targetdf.columns},inplace=True)
            targetdf = targetdf.join(classeddf)
            
            print(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt)
            targetdf.drop(columns=[col for col in targetdf.columns if 'client' in col and 'clssd' not in col],inplace=True)
            targetdf.rename(columns={col:col.replace('clssd','') for col in targetdf.columns if 'client' in col},inplace=True)
            if not debugmode: targetdf[listOfColsWeWantToOutput].to_csv(momentumraSzurtSzokeresesPath+preMomFile+filenamecore+postMomFileSzurt,index=False)
            #targetdf[listOfColsWeWantToOutput].to_csv('probaout.csv',index=False)
         
    sf.doThisWhenNoFileIsFoundToProcess()


# In[ ]:




