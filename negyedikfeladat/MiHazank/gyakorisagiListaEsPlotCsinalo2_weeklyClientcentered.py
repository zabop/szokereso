#!/usr/bin/env python
# coding: utf-8

# In[1]:


clientName = 'MiHazank'


# In[2]:


import pandas as pd
import glob
import datetime
import time
import matplotlib.pyplot as plt


# In[7]:


def generateFreqRes(filesThatDate,date):
#    print(date)
    dfs = [pd.read_csv(file) for file in filesThatDate]
    df = pd.concat([df[col] for df in dfs for col in df.columns if 'client' in col])
    df_value_counts = df.value_counts()
    df_value_counts.sort_values(ascending=True).to_csv(freqFilesPath+'weeklyfreqfile_'+str(date).split(' ')[0]+'.csv')
    plot = pd.read_csv(freqFilesPath+'weeklyfreqfile_'+str(date).split(' ')[0]+'.csv',index_col=0).plot.barh(legend=False)
    fig = plot.get_figure()
    fig.savefig(freqFilesPath+'barplot_'+str(date).split(' ')[0]+'.png', bbox_inches='tight')
    plt.close()


# In[8]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern,cutoffdate):
    
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(int(each.split('/')[-1][37:41]),
                                 int(each.split('/')[-1][42:44]),
                                 int(each.split('/')[-1][45:47]),
                                 int(each.split('/')[-1][48:50]),
                                 int(each.split('/')[-1][51:53])) for each in csvs]

    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt >= datetime.datetime(*cutoffdate)]
    
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    
    return sorted_filtered_csvs


# In[9]:


def getFilesOnGivenWeek(dayOfFirstDayOfWeek):
    
    sevenDayAfterDay = dayOfFirstDayOfWeek + datetime.timedelta(days=7)
    
    return list(
    set(get_files_sorted_by_date_after_a_date(momFilesPathAndWildCard,[dayOfFirstDayOfWeek.year,
                                                                       dayOfFirstDayOfWeek.month,
                                                                       dayOfFirstDayOfWeek.day,0]))-\
    set(get_files_sorted_by_date_after_a_date(momFilesPathAndWildCard,[sevenDayAfterDay.year,
                                                                       sevenDayAfterDay.month,
                                                                       sevenDayAfterDay.day,0])))


# In[10]:


def doThisWhenNotEnoughFilesForWeek(sleepThisMuch=60*60,day=None):
    print('Not enough files found. '+str(day)+' Sleeping '+str(sleepThisMuch/60)+' minutes.')
    time.sleep(sleepThisMuch)


# In[11]:


def didMoreThanThisManySecondsElapsedSinceEndOfThatWeek(singleDate,seconds):
    return (datetime.datetime.now() - (singleDate + datetime.timedelta(days=7))).total_seconds() > seconds


# In[12]:


freqFilesPath = '/mnt/volume/jupyter/szokereso/negyedikfeladat/'+clientName+'/szokeresores/weeklyfreqs/'
momFilesPathAndWildCard  = '/mnt/volume/jupyter/szokereso/negyedikfeladat/'+clientName+'/szokeresores/clientreszurt/live_updated3_dict_only_1client_data_*_dfUnifiedNanFilteredOnlySomeColsUpdated3.csv'


# In[13]:


start_date = datetime.datetime(2020,6,29)
week_count = 100

for single_date in (start_date + datetime.timedelta(7*n) for n in range(week_count)):
    while True:
        filesThatDate = getFilesOnGivenWeek(single_date)
        if len(filesThatDate) < 12*7 and not didMoreThanThisManySecondsElapsedSinceEndOfThatWeek(single_date, 600):
            doThisWhenNotEnoughFilesForWeek(sleepThisMuch=120*60,day=single_date)
        else:
            generateFreqRes(filesThatDate,single_date)
            print(single_date)
            break


# In[ ]:




