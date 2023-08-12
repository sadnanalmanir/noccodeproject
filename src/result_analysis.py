#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import os
from pyprojroot import here

# Linux directory
#os.chdir(r'/home/sadnan/PycharmProjects/noccodeproject')
#os.chdir(r'/home/sadnan/Downloads/NOC_Code_Program')
#os.chdir(r'/home/sadnan/Downloads')

# df = pd.read_csv('title_noc_result_byprogram.csv')
df = pd.read_csv(here() / 'title_noc_result_byprogram.csv')

#if not df.empty:
#    print('success reading')

df['fourth digit'] =1
df['third digit'] = 1
df['second digit'] =1
df['first digit'] = 1
df['noc flag'] = 1
df['note flag'] = df['note']



df.loc[df['fourth position'].isna(), 'fourth digit']=0
df.loc[df['third position'].isna(), 'third digit']=0
df.loc[df['second position'].isna(), 'second digit']=0
df.loc[df['first position'].isna(), 'first digit']=0
df.loc[df['noc flag'].isna(), 'noc flag']=0
df.loc[df['note'].isna(), 'note flag']='original'

df[['noc flag','first digit','second digit','third digit','fourth digit','weight','note flag']]

#print(df.columns)

df_fourth= df.loc[(df['fourth digit']==1),['note flag','fourth digit']].groupby('note flag').count()
df_third= df.loc[(df['third digit']==1),['note flag','third digit']].groupby('note flag').count()
df_second= df.loc[(df['second digit']==1),['note flag','second digit']].groupby('note flag').count()
df_one= df.loc[(df['first digit']==1),['note flag','first digit']].groupby('note flag').count()

#print(df_fourth)

print('Fourth digit')
print('Sum',df_fourth['fourth digit'].sum(),'Percentage',df_fourth['fourth digit'].sum()/len(df))
print(' ')
print('Third digit')
print('Sum',df_third['third digit'].sum(),'Percentage',df_third['third digit'].sum()/len(df))
print(' ')
print('Second digit')
print('Sum',df_second['second digit'].sum(),'Percentage',df_second['second digit'].sum()/len(df))
print(' ')
print('First digit')
print('Sum',df_one['first digit'].sum(),'Percentage',df_one['first digit'].sum()/len(df))
print(' ')