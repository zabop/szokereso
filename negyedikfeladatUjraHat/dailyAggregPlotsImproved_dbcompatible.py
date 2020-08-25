#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import datetime
import time
import matplotlib.pyplot as plt
import pathlib
import re


# In[2]:


path=str(pathlib.Path().absolute())


# In[3]:


excelFile='/mnt/volume/jupyter/szokereso/vip_szotar_1.4.xlsx'


# In[4]:


def doneTheseDays(client):

    pngs = glob.glob(client+'/szokeresores/dailyfreqs/*png')
    csvs = glob.glob(client+'/szokeresores/dailyfreqs/*csv')
    
    csvdates = [datetime.datetime(*[int(num) for num in re.findall(r'\d+', filename)]) for filename in csvs]
    pngdates = [datetime.datetime(*[int(num) for num in re.findall(r'\d+', filename)]) for filename in pngs]
    
    csvAndPngDates = list(set.intersection(set(csvdates),set(pngdates)))
    
    return csvAndPngDates


# In[5]:


def generateFreqRes(filesThatDate,date,freqFilesPath,debugmode=True):        
    dfs=[]
    for file in filesThatDate:
        try:
            dfs.append(pd.read_csv(file))
        except pd.io.common.EmptyDataError:
            print('EmptyDataError: '+file)

    try:
        df = pd.concat([df[col] for df in dfs for col in df.columns if 'client' in col])
        df_value_counts = df.value_counts()
        
        if not debugmode: 
            df_value_counts.rename_axis('PLACEHOLDER1')                           .reset_index()                           .rename(columns={0:'PLACEHOLDER2'})                           .sort_values(by='PLACEHOLDER2',ascending=True)                           .to_csv(freqFilesPath+'dailyfreqfile_'+str(date).split(' ')[0]+'.csv',index=False)
    except ValueError:
        pass
    try:
        #plot = pd.read_csv(freqFilesPath+'dailyfreqfile_'+str(date).split(' ')[0]+'.csv').plot.barh()
        plot = pd.read_csv(freqFilesPath+'dailyfreqfile_'+str(date).split(' ')[0]+'.csv',index_col=0).plot.barh(legend=False)
        plot.yaxis.label.set_visible(False)
        fig = plot.get_figure()
        if not debugmode: fig.savefig(freqFilesPath+'barplot_'+str(date).split(' ')[0]+'.png', bbox_inches='tight')
        plt.close()
    except TypeError:
        pass


# In[6]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern, cutoffdate):
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(*[int(num) for num in re.findall(r'\d+', each)[:4]]) for each in csvs]
    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt >= datetime.datetime(*cutoffdate)]
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    return sorted_filtered_csvs


# In[7]:


def getFilesOnGivenDate(day,momFilesPathAndWildCard):
    
    dayafterday = day + datetime.timedelta(days=1)
    
    return list(
    set(get_files_sorted_by_date_after_a_date(momFilesPathAndWildCard,[day.year,day.month,day.day,0]))-\
    set(get_files_sorted_by_date_after_a_date(momFilesPathAndWildCard,[dayafterday.year,dayafterday.month,dayafterday.day,0])))


# In[8]:


def doThisWhenNotEnoughFilesForDay(sleepThisMuch=60*60,day=None):
    #print('Not enough files found. '+str(day)+' Sleeping '+str(sleepThisMuch/60)+' minutes.')
    print('Looped through all clients. Sleeping ' + str(sleepThisMuch / 60) + ' minutes')
    time.sleep(sleepThisMuch)


# In[9]:


def didMoreThanThisManySecondsElapsedSinceEndOfThatDay(singleDate,seconds):
    return (datetime.datetime.now() - (singleDate + datetime.timedelta(days=1))).total_seconds() > seconds


# In[10]:


def getClients(excelFile=excelFile):
        
    xl = pd.ExcelFile(excelFile)
    sheetNames = [sheetName.strip() for sheetName in xl.sheet_names]
        
    return sheetNames


# In[11]:


def szokeresoIsUnlikelyToRunRightNow():
    now = datetime.datetime.now()
    if now.hour % 2 == 0 and now.minute<15:
        return False
    else:
        return True


# In[12]:


clients = getClients()

while True:
    
    if szokeresoIsUnlikelyToRunRightNow():
    
        for client in clients:

            freqFilesPath = path+'/'+client+'/szokeresores/dailyfreqs/'
            momFilesPathAndWildCard  = path+'/'+client+'/szokeresores/clientreszurt/live_*_szurt.csv'

            start_date = datetime.datetime(2020,7,1)
            day_count = 10000

            doneThese = doneTheseDays(client)
            for single_date in (start_date + datetime.timedelta(n) for n in range(day_count)):
                if single_date not in doneThese:
                    filesThatDate = getFilesOnGivenDate(single_date,momFilesPathAndWildCard)
                    if len(filesThatDate) < 12 and not didMoreThanThisManySecondsElapsedSinceEndOfThatDay(single_date, 600):
                        #doThisWhenNotEnoughFilesForDay(sleepThisMuch=10*60,day=single_date)
                        break
                    else:
                        generateFreqRes(filesThatDate,single_date,freqFilesPath,debugmode=False)
                        print(client)
                        print(single_date)

        doThisWhenNotEnoughFilesForDay(sleepThisMuch=10*60,day=single_date)
    else:
        print('We are within 15 minutes of an even hour. Waiting until szokereso is surely finished. Sleeping 5 mins.')
        time.sleep(5*60)


# In[ ]:





# In[ ]:





# In[ ]:




