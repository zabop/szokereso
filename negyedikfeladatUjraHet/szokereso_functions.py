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


# In[3]:


def didMoreThanThisManySecondsElapsedSinceEndOfThatDay(singleDate,seconds):
    '''
    datetime.datetime.now() returns an object like this:
        datetime.datetime(2020, 8, 17, 9, 26, 21, 78730)

    '''

    return (datetime.datetime.now() - (singleDate + datetime.timedelta(days=1))).total_seconds() > seconds


# In[6]:


#def getSearchListFromTabName(tabName,pathToExcelFile=excelFile):
def getSearchListFromTabName(tabName,excelFile):
    '''
    Example usage: getSearchListFromTabName('LMP') returns:

    [['LMP', 'Lehet Más A Politika'],
     ['Csárdi Antal', 'Csárdi'],
     ['Demeter Márta', 'Demeter'],
     ['Ungár Péter', 'Ungár']]

    The excel file on the LMP tab looks like this, compare:
    https://raw.githubusercontent.com/zabop/szokeresoDocs/master/howTheSzotarLooksLike.png

    pd.ExcelFile() reads in the whole excel file, with all tabs.

    dfs is a dict created with a dict comprehension.
    Keys are tab names of the excel file.
    Values are the list of lists, one shown above. 

    xl.parse(sheetname.header=None) returns a dataframe.
    If not all rows have equal number of columns, nans will appear.
    For example: xl.parse('MSZP',header=None).values.tolist() returns:

    [['MSZP', 'Magyar Szocialista Párt', nan, 'Szocik'],
     ['Ujhelyi István', 'Ujhelyi', nan, nan],
     ['Kunhalmi Ágnes', 'Kunhalmi', nan, nan],
     ['Hiller István', 'Hiller', nan, nan],
     ['Molnár Gyula', nan, nan, nan],
     ['Bangóné Borbély Ildikó', 'Bangóné', nan, nan],
     ['Mesterházy Attila', 'Mesterházy', nan, nan],
     ['Tóth Bertalan', nan, nan, nan],
     ['Tóth Csaba', nan, nan, nan],
     ['Tüttő Kata', 'Tüttő', nan, nan]]

    The MSZP tab looks like this in the original excel file:
    https://raw.githubusercontent.com/zabop/szokeresoDocs/master/tabMSZP.PNG
    We can see that C1 is unreasonably left blank, but so the first line includes a nan in the third place.
    There are other nans too, which we wouldn't want to return.

    for person in xl.parse(sheetname,header=None).values.tolist() is looping through each list.
    Ie first item:
    ['MSZP', 'Magyar Szocialista Párt', nan, 'Szocik']
    second item:
    ['Ujhelyi István', 'Ujhelyi', nan, nan].

    [alias for alias in person if type(alias) is not float] is looping through these lists.
    Ie first item:
    MSZP
    second item:
    'Magyar Szocialista Párt'
    third item:
    nan.

    The result of this inner list comprehension is a list not containing nans, by the filtering them out: if not float.

    dfs will contain this for every tab of the excel file. We only return one value of the dfs dict.

    getSearchListFromTabName('MSZP') will return:
    [['MSZP', 'Magyar Szocialista Párt', 'Szocik'],
     ['Ujhelyi István', 'Ujhelyi'],
     ['Kunhalmi Ágnes', 'Kunhalmi'],
     ['Hiller István', 'Hiller'],
     ['Molnár Gyula'],
     ['Bangóné Borbély Ildikó', 'Bangóné'],
     ['Mesterházy Attila', 'Mesterházy'],
     ['Tóth Bertalan'],
     ['Tóth Csaba'],
     ['Tüttő Kata', 'Tüttő']]

    We are doing more calculation than strictly needed.
    We are returning only one value from a dict, but creating the whole dict.
    This isn't a performance-limiting issue though, as this operation is performed once per tab.
    The potential runtime gain by doing this better is in the order of, so we don't care.

    (If bothered, try tabName == sheetname at the end of dict comprehension, but haven't tested this.)

    The commented out line after DONT DO THIS includes a .dropna(), which is not behaving as would be desired here.
    It drops every row with a nan, the entire row, not just the nans from it.
    '''    
    pathToExcelFile=excelFile
    xl = pd.ExcelFile(pathToExcelFile)
    #dfs = {sheetname: xl.parse(sheetname, header=None).dropna().values.tolist() for sheetname in xl.sheet_names}
    dfs = {sheetname: [[alias for alias in person if type(alias) is not float]
                              for person in xl.parse(sheetname,header=None).values.tolist()]
                              for sheetname in xl.sheet_names}
    return dfs[tabName]


# In[7]:


def validalias(alias, strict=False):
    '''
    Some dictionaries contain aliases which we didn't want to use.
    In this case, we use the strict mode. Default is not strict mode, so every alias is valid.

    (By dictionaries I mean list of entities, each entity having different names, ie 'MSZP', 'Magyar Szocialista Párt', 'Szocik'.
    The different aliases in this case is 'MSZP', 'Magyar Szocialista Párt', 'Szocik', entity is: 'MSZP')

    Filtering conditions in strict mode:

    - it had to be longer than 5 characters without trailing and leading spaces
    - it had to be at least a bigram, ie at least one space between first and last non-space character

    Ilénke isn't a valid alias, Nagy Ilén is.
    '''
    
    if not strict:
        return True
    if strict:
        if len(str(alias).strip()) > 5 and len(str(alias).strip().split(' ')) > 1: return True
        else: return False


# In[9]:


def matchfinder(text,searchforthese,strictfiltering=False):
    '''
    This function uses list comprehensions on nested lists.
    A good visualization on how that works: https://i.stack.imgur.com/0GoV5.gif
    From here: https://stackoverflow.com/a/45079294/8565438. I recommend to understand this answer.

    We iterate through searchforthese, which is a list of alias lists, ie:

    [['LMP', 'Lehet Más A Politika'],
     ['Csárdi Antal', 'Csárdi'],
     ['Demeter Márta', 'Demeter'],
     ['Ungár Péter', 'Ungár']]

    persondata_searchtarget is the individual alias lists, (ie ['LMP', 'Lehet Más A Politika'], then ['Csárdi Antal', 'Csárdi']).
    We iterate through these (ie take LMP, then Lehet Más A Politika) & check for conditions.

    If these conditions are fulfilled, the alias which fulfilled those conditions will be part of mathces.

    These contitions:
    The alias should be a valid alias (ie validalias(alias) should be True)
    alias.lower() in str(text).lower() should be True.

    'ElEfÁnT'.lower() is elefánt: lowercasing both alias & text is used to avoid inconsistencies in capitalization.
    str(np.nan) is 'nan'. It is used in case input data contains nans, which potentially screws up the function.

    Example:

    matchfinder('LMP, legyen meleg Péter, Csárdi Antal nem csárdi', [['LMP', 'Lehet Más A Politika'],
                                                                     ['Csárdi Antal', 'Csárdi'],
                                                                     ['Demeter Márta', 'Demeter'],
                                                                     ['Ungár Péter', 'Ungár']])

    Returns: ['LMP', 'Csárdi Antal', 'Csárdi'].

    We see that occasionally we detect a false positive: here, be returning csárdi.
    If we don't lowercase everything, we'll have false negatives.
    Make your choices.
    '''    
    matches=[alias
             for persondata_searchtarget in searchforthese
             for alias in persondata_searchtarget
             if validalias(alias,strict=strictfiltering) and alias.lower() in str(text).lower()]
    return matches


# In[10]:


class dictionary_class:
    '''
    Each dictionary has a name, maxcolnum, searchlist, geo attributes.
    
    name: the name of the dictionary
    
    maxcolnum: the maximum number of different entries we want to find in a text
    If we find more, we will say we haven't found any of them.
    (This is to tackle texts which were signed by a lot of people but is not about those people.)
    searchlist is the list of alias lists, ie:
    
     [['LMP', 'Lehet Más A Politika'],
      ['Csárdi Antal', 'Csárdi'],
      ['Demeter Márta', 'Demeter'],
      ['Ungár Péter', 'Ungár']]
    
    geo is a boolean, refering to a dictionary containing geographical names.
    They are treated differently to people's names sometimes.
    
    '''    
    def __init__(self, name, maxcolnum, searchlist=None, geo=False):
        self.name = name
        self.maxcolnum = maxcolnum
        self.searchlist = searchlist
        self.geo = geo


# In[13]:


def get_files_sorted_by_date_after_a_date(look_for_this_pattern, cutoffdate):
    '''
    look_for_this_pattern should be a wildcard, ie: '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
    cutoffdate should be a list in the format of [year, month, day, 0], ie: [2020,7,1,0]
    
    csvs will be a list of files like this, with the example look_for_this_pattern wildcard above:
    
    ['/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-08-17_16:01:34.csv',
     '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-27_06:00:42.csv',
     '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-26_22:00:58.csv',
     ...]
     
    These are the scraped input files.
    They are generated every two hours.
    data_2020-07-26_22:00:58.csv was generated (roughly) at 2020 July 22th 22h, & it took 00:58 to produce the file.
     
    re.findall(r'\d+', each) finds all the digits in the variable each.
    Source: https://stackoverflow.com/a/4289348/8565438

    Examples:
    
    re.findall(r'\d+', 'A 3 kismalac és az 1 farkas meséjének 10edik változata')
    returns:
    ['3', '1', '10']
    
    re.findall(r'\d+', '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-08-17_16:01:34.csv')
    returns:
    ['2020', '08', '17', '16', '01', '34']
    
    
    |   !!!WARNING!!!:
    |   DO NOT USE NUMERAL CHARACTERS IN PATH LEADING TO INPUT FILES.
    |   For example:
    |   re.findall(r'\d+', '/mnt/volume/anagy/mediascraper/mediaScraper/output2/data_2020-08-17_16:01:34.csv')
    |   returns:
    |   ['2', '2020', '08', '17', '16', '01', '34']
    |   The '2' in the front is clearly not what we want.
    
    
    The inner list comprehension converts these to ints.
    The first 4 element of this list is what we care about, so we include the [:4].
    
    datetimes will be a list of datetime.datetime objects, for example, one element of the list can be:
    datetime.datetime(2020, 8, 17, 16, 0)
    The * used in creation of datetimes list is to unpack argument lists, as described in this answer, for example:
    https://stackoverflow.com/a/36908/8565438
    
    dt_csvs_filtered will be a list of lists.
    These lists will contain a datetime.datetime object & the csv file it was created from.
    dt_csvs_filtered will only contain those lists which had a datetime.datetime object in them satisfying a condition.
    Condition: datetime.datetime object within list must reference a later point in time than datetime.datetime(*cutoffdate).
    
    sorted_filtered_csvs is the csv filenames from the dt_csvs_filtered list.
    They are sorted by chronologically using the datetime.datetime objects within dt_csvs_filtered.
    More detailed description here: https://stackoverflow.com/a/6618543/8565438
    '''
    csvs = glob.glob(look_for_this_pattern)
    datetimes=[datetime.datetime(*[int(num) for num in re.findall(r'\d+', each)[:4]]) for each in csvs]
    dt_csvs_filtered=[[dt, csv] for dt, csv in zip(datetimes,csvs) if dt >= datetime.datetime(*cutoffdate)]
    sorted_filtered_csvs = [csv
                        for _, csv in sorted(
                                         zip([eachpair[0] for eachpair in dt_csvs_filtered],
                                             [eachpair[1] for eachpair in dt_csvs_filtered]))]
    return sorted_filtered_csvs


# In[14]:


#def pathFinder(clientName,path=str(pathlib.Path().absolute())):
def pathFinder(clientName,path):
    '''
    This function is to return strings used in paths, filenames, wildcards.
    
    #str(pathlib.Path().absolute()) returns the directory which the code is run from, without final /.
    #Ie str(pathlib.Path().absolute()):
    #'/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNegy'
    #In the same Jupyter Notebook, !pwd is:
    #/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNegy
    ''' 
    preMomFile = 'live_'
    postMomFileSzokereso = '_szokereso_result.csv'
    postMomFileSzurt = '_szurt.csv'
    postMomFileErrorlog = '_ERRORLOG.txt'

    inputPathAndWildcard = '/mnt/volume/anagy/mediascraper/mediaScraper/output/data*csv'
    szokeresoResFilesPath =   path+'/'+clientName+'/szokeresores/'
    momentumraSzurtSzokeresesPath    = szokeresoResFilesPath + 'clientreszurt/'
    szokeresoResFilesPathAndWildcard = momentumraSzurtSzokeresesPath + preMomFile + '*' + postMomFileSzurt

    return preMomFile, postMomFileSzokereso, inputPathAndWildcard, postMomFileSzurt, szokeresoResFilesPath, szokeresoResFilesPathAndWildcard, momentumraSzurtSzokeresesPath


def getOutputFiles(pathAndWildcard):
    '''
    Returning files the script outputted.
    '''    
    outputFiles = glob.glob(pathAndWildcard)
    return outputFiles


# In[16]:


def getTodoFilesWithoutOutput(todoFiles,outputFiles):
    '''
    todoFiles is a list of files which we want to have performed operations on.
    outputFiles is a list of files resulting from these operations.
    
    Example usage:
    
    getTodoFilesWithoutOutput(todoFiles=['/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-01_00:00:24.csv',
                                     '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-01_02:00:18.csv',
                                     '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-01_04:00:22.csv'],
                              outputFiles=['live_data_2020-07-01_00:00:24_szurt.csv'])
                              
    todoFiles is looped through, & upon fulfilling a condition, each todoFile is put back to the list:
    [todoFile for todoFile in todoFiles if condition]
    The condition is:
    not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in outputFiles])
    
    If todoFile is: '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-01_00:00:24.csv'
    todoFile.split('/')[-1].split('.')[0] is: 'data_2020-07-01_00:00:24'
    
    todoFile.split('/')[-1].split('.')[0] in szokeresoOutput is a boolean.
    If szokeresoOutput is 'live_data_2020-07-01_00:00:24_szurt.csv'.
    
    Example:
    'data_2020-07-01_00:00:24' in szokeresoOutput
    is evaluated to be True.
    
    'data_2020-07-01_04:00:22' in szokeresoOutput
    is ecaluated to be False.
    
    By looping through all the outputfiles, we produce a list of booleans:
    [todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in outputFiles]
    The nth element of this list is True if the nth element of outputFiles is the output corresponding to input file todoFile.
    
    WARNING: be cautious when renaming outputfiles, not to screw up the functionality of this function.
    
    If any element of this list if True, there is an output for corresponding to todoFile.
    Therefore, we want to return todoFile only if not any of the elements of this list is True:
    if not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in outputFiles])]
    
    for any(), see: https://docs.python.org/3/library/functions.html#any
    '''    
    return [todoFile for todoFile in todoFiles
           if not any([todoFile.split('/')[-1].split('.')[0] in szokeresoOutput for szokeresoOutput in outputFiles])]

def prepareDirectoryTreeAndReturnDfs(excelFile,path):
#def prepareDirectoryTreeAndReturnDfs(excelFile=excelFile):
    '''
    xl is reads in the excel file with multiple sheets.
    sheetNames is the name of the different sheets in the excel file
    The dict comprehension separates xl to different dataframes within a dict.
    Key for these dicts are the names of the worksheets.
    
    Take care not to have any headers in the excel file on any of the worksheets.
    
    #section below no longer applicable
    #str(pathlib.Path().absolute()) is the path without the final '/' where the script is being run.
    #Ie:
    #str(pathlib.Path().absolute()) is '/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHet'
    #
    #WARNING: KEEP THE szokereso_functions FILE WHERE THE szokereso_core IS, to make sure this path variable is right.
    #Haven't tested what happens if you don't do it, don't try without making sure you don't screw stuff up.
    #section no longer applicable above
    
    The final double for loop crates a directory for every client.
    Within these directories, there a
    szokeresores/clientreszurt,
    szokeresores/dailyfreqs,
    szokeresores/weeklyfreqs
    is created.
    
    This is where the outputs are heading.
    '''
        
    xl = pd.ExcelFile(excelFile)
    sheetNames = [sheetName.strip() for sheetName in xl.sheet_names]
    dfs = {sheetname.strip():
           xl.parse(sheetname,header=None)
           for sheetname in xl.sheet_names}          
    
    path_slash=path+'/'
    for sheetName in sheetNames:
        for subdir in ['clientreszurt','dailyfreqs','weeklyfreqs']:
            os.makedirs(path_slash+sheetName+'/'+'szokeresores/'+subdir, exist_ok=True)
            
    print('Directory tree has been built here: '+path_slash)
    print('(If you want to build it somewhere else, make sure  this function is in the directory you want the directory tree to be in.)')
          
    return dfs

def equivalences(df, equivalenceClasses):
    '''
    For details on how this function works, see the answers this question:
    https://stackoverflow.com/questions/63237043/how-to-get-columns-containing-names-of-pre-defined-equivalence-classes-of-values
    '''
    d = dict(ChainMap(*[dict.fromkeys(y,x) for x , y in equivalenceClasses.items()]))
    df = df.replace(d)
    df = df.mask(df.apply(pd.Series.duplicated,1))
    return df


def getEquivalenceClasses(df):
    '''
    Takes a dataframe, creates a dict of equivalence classes.
    Each row of the dataframe is put to a distinct equivalence class.
    The name of each equivalence class is the first element of the row.

    YOU SHOULD NOT HAVE MULTIPLE ROWS STARTING WITH THE SAME STRING (ie one person should appear only once in the dict)

    Each equivalence class is a list of elements which are said to be equivalent.

    Example:

    Suppose we have a dataframe df:

    +----+---------------+----------------------+
    |    | 0             | 1                    |
    |----+---------------+----------------------|
    |  0 | LMP           | Lehet Más A Politika |
    |  1 | Csárdi Antal  | Csárdi               |
    |  2 | Demeter Márta | Demeter              |
    |  3 | Ungár Péter   | Ungár                |
    +----+---------------+----------------------+

    dict(zip(df[0],df.values.tolist())) will yield:

    {'LMP': ['LMP', 'Lehet Más A Politika'],
     'Csárdi Antal': ['Csárdi Antal', 'Csárdi'],
     'Demeter Márta': ['Demeter Márta', 'Demeter'],
     'Ungár Péter': ['Ungár Péter', 'Ungár']}

    (Pretty-printing outlined in this Q: https://stackoverflow.com/questions/63547508/how-to-read-in-pretty-printed-dataframe-into-a-pandas-dataframe)
    
    SO post explaining how it works:
    https://stackoverflow.com/questions/63548321/pandas-dataframe-rows-to-dict-of-lists-using-first-value-of-each-row-as-key
    ''' 
    #equivalenceClasses = {row[1][0]: list(row[1]) for row in df.iterrows() for alias in row[1]}    
    equivalenceClasses = dict(zip(df[0],df.values.tolist()))
    return equivalenceClasses

def doThisWhenNoFileIsFoundToProcess(sleepThisMuch=5*60):
    #print('No more files found to process. Sleeping '+str(sleepThisMuch)+' seconds.')
    '''
    Sleeps as many seconds as its argument. 
    '''
    print('Looped through all clients. Sleeping '+str(sleepThisMuch)+' seconds.')
    time.sleep(sleepThisMuch)

    
def filetime(file):
    '''
    For example, if this filename used as input:
    '/mnt/volume/anagy/mediascraper/mediaScraper/output/data_2020-07-01_02:00:18.csv'
    this fuction returns:
    [2020, 7, 1, 2]

    Based on:
    https://stackoverflow.com/a/4289348/8565438
    '''
    year, month, day, hour = re.findall(r'\d+', file.split('/')[-1])[:4]
    return [int(each) for each in [year, month, day, hour]]