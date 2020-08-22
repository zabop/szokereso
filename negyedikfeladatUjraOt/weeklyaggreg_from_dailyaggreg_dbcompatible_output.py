#!/usr/bin/env python
# coding: utf-8

# In[161]:


import pandas as pd
import glob
import re
import datetime
import matplotlib.pyplot as plt
import time
from datetime import date, timedelta


# In[162]:


def weeknum(dayname):
    if dayname == 'Monday':   return 0
    if dayname == 'Tuesday':  return 1
    if dayname == 'Wednesday':return 2
    if dayname == 'Thursday': return 3
    if dayname == 'Friday':   return 4
    if dayname == 'Saturday': return 5
    if dayname == 'Sunday':   return 6


# In[163]:


def alldays(year, whichDayYouWant):
    d = date(year, 1, 1)
    d += timedelta(days = (weeknum(whichDayYouWant) - d.weekday()) % 7)
    while d.year == year:
        yield d
        d += timedelta(days = 7)


# In[164]:


def weeknumber(year, month, day, weekstartsonthisday):
    specificdays = [d for d in alldays(year, weekstartsonthisday)]
    return len([specificday for specificday in specificdays if specificday <= datetime.date(year,month,day)])


# In[155]:


dailyaggregfiles = glob.glob('*/szokeresores/dailyfreqs/*csv')
df = pd.DataFrame(dailyaggregfiles,columns=['dailyaggregfiles'])


# In[156]:


df['client']         = df.apply(lambda r:r['dailyaggregfiles'].split('/')[0],axis=1)
df['dt']             = df.apply(lambda r:datetime.datetime(*[int(e) for e in re.findall(r'\d+',r['dailyaggregfiles'])]),axis=1)
df['yearWeekFridayThursday'] = df['dt'].apply(
                                lambda r: '_'.join([str(r.year),
                                                    str(weeknumber(r.year,r.month,r.day,'Friday'))]))
df['yearWeekFridayThursdayClient'] = df.apply(
                                lambda r: r['yearWeekFridayThursday']+'_'+r['client'],axis=1)
df.drop(columns=['client','dt','yearWeekFridayThursday'],inplace=True);


# In[157]:


gb = df.groupby('yearWeekFridayThursdayClient')
dfsByWeekByClient = {group:gb.get_group(group) for group in gb.groups}


# In[166]:


weeklyAggregDfByWeekByClient = {key:pd.concat(pd.read_csv(each) for each in value['dailyaggregfiles'])                                    .groupby('PLACEHOLDER1')                                    .sum()                                    .sort_values(by='PLACEHOLDER2')                                    .reset_index()
                               for key, value in zip(dfsByWeekByClient.keys(), dfsByWeekByClient.values())}


# In[167]:


def writeOutAndPlot(dfdict, key, debugmode=True):
    dfdict[key].plot.barh(x='PLACEHOLDER1',y='PLACEHOLDER2',legend=False)
    plt.xlabel('mentions')
    plt.ylabel('who');
    plt.tight_layout()
    print((lambda key: key.split('_')[-1]+'/szokeresores/weeklyfreqs/'+'_'.join(key.split('_')[:2])+'.png')(key))
    if not debugmode:
        plt.savefig((lambda key: key.split('_')[-1]+'/szokeresores/weeklyfreqs/'+'_'.join(key.split('_')[:2])+'_FridayThursday.png')(key))
        dfdict[key].to_csv(
            (lambda key: key.split('_')[-1]+'/szokeresores/weeklyfreqs/'+'_'.join(key.split('_')[:2])+'_FridayThursday.csv')(key),
            index=False)
    plt.close()


# In[ ]:


while True:
    yr,week,hour=datetime.datetime.now().isocalendar()[0],datetime.datetime.now().isocalendar()[1],datetime.datetime.now().hour
    for key in weeklyAggregDfByWeekByClient.keys():
        if key.split('_')[0] != yr and key.split('_')[1] != week and not hour < 3:
            writeOutAndPlot(weeklyAggregDfByWeekByClient, key, debugmode=False)
            print('hw')
            #break#deletewhenrunlive
    #break#deletewhenrunlive
    time.sleep(3*60*60)


# In[ ]:




