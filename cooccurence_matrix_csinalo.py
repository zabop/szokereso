#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd


# In[ ]:


df=pd.read_csv('resultfiles/data_2020-06-28_08:01:41_szokereso_result.csv')


# In[ ]:


dictstrings = ['person_data', 'wikilist','stanza','settlement_list']
dictcols=[col for col in df.columns if any([dictstring in col for dictstring in dictstrings])]


# In[ ]:


uniques=pd.concat([df[col] for col in dictcols]).dropna().unique()


# In[ ]:


cooc = pd.DataFrame(index=uniques, columns=uniques)


# In[ ]:


for icoocrow, coocrow in enumerate(cooc.index):
    for icooccol, cooccol in enumerate(cooc.columns):
        if icoocrow ==icooccol: print(icoocrow/5878)
        if icoocrow > icooccol:
            count=0
            for index, row in df[[*dictcols]].iterrows():
                if cooccol in list(row) and coocrow in list(row):
                    count+=1
            cooc.loc[coocrow,cooccol]=count


# In[ ]:


cooc=cooc.fillna(0)


# In[ ]:


cooc=cooc+cooc.transpose()


# In[ ]:


cooc.to_csv('resultfiles/data_2020-06-28_08:01:41_szokereso_result_cooc.csv')

