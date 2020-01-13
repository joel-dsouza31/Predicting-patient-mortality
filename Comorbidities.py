#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.display import display_html
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import math


host='localhost'
database='eicu'
username='purav'
port = "5432"

postgres_str =('postgresql://'+username+':root'+'@'+host+':'+port+'/'+database)
#   Create the connection
cnx = create_engine(postgres_str)


# In[2]:


dfcomo = pd.read_csv('comorbidities.csv',sep=' ')
como_dict = {}


# In[3]:


#creating a dictionary for the codes
def create_dict():
    for i in range(len(dfcomo[['codes']])):
        codes = (dfcomo[['codes']].loc[i][0]).split(',')
        temp_dict = {dfcomo[['comorbidity']].loc[i][0]:codes}
        como_dict.update(temp_dict)
    extending(como_dict)


# In[4]:


#extend with .x values:
def extending(como_dict):
    for keys in como_dict:
        val_list = como_dict[keys]
        for items in val_list:
            check = items.split('.')
            if(check[1] == 'x'):
                front = int(check[0])
                for i in range(100):
                    val_list.append(str(front + (i/100)))    


# In[5]:


#final dataframe with comorbidities as features
def final_dataframe():
    comorbidities = dfcomo[['comorbidity']].values
    col = ["Patient"]
    for i in range(len(comorbidities)):
        col.append(comorbidities[i][0])
    col.append("Total")
    fdf = pd.DataFrame(columns=col)
    return(fdf)


# In[6]:


create_dict()
fdf = final_dataframe()


# In[18]:


#calculate score
def elix_score(patient,icd_list):
    score = 0
    comor_list = []
    #for each icd code find its weight
    for val in icd_list:
        for keys, values in como_dict.items():
            for items in values:
                if items == val:
                    comor_list.append(keys)
    rep_list = list(set(comor_list))
    for comor in rep_list:
        ind = dfcomo.index[dfcomo['comorbidity'] == comor]
        weight = dfcomo['weight'][ind]
        score = score + weight.values[0]
        
    return_df = update_fdf(patient,comor_list,score)
    return(return_df)


# In[8]:


def update_fdf(patient,comor_list,score):
    temp_dict = {}
    temp_dict["Patient"] = int(patient)
    temp_dict["Total"] = int(score)
    for comor in comor_list:
        temp_dict[comor] = 0
    for comor in comor_list:
        temp_dict[comor] = temp_dict[comor]+1
    temp_df = fdf.append(temp_dict,ignore_index=True)
    temp_df = temp_df.fillna((int)(0))
    return(temp_df)


# In[14]:


diagnosis = pd.read_sql('Select patientunitstayid,icd9code from eicuu.diagnosis',cnx)
diagnosis_len = len(diagnosis.index)
print(diagnosis_len)


# In[15]:


diagnosis_len = len(diagnosis.index)
dictionary = {}

for i in range(diagnosis_len):
    dictionary[diagnosis.iloc[i][0]]=[]
    


# In[16]:


count=0
for i in range(diagnosis_len):
    count+=1
    print(count)
    codes = diagnosis.iloc[i][1].split(',')
    icd9 = codes[0]
    icd9= icd9.strip()
    if icd9!="" and icd9[0].isdigit():
        dictionary[diagnosis.iloc[i][0]].append(icd9)


# In[17]:


df = pd.DataFrame(list(dictionary.items()), columns=['patientunitstayid', 'icd9'])
df.to_csv("patient_icd.csv")
d = {}
for i in df['patientunitstayid'].unique():
    d[i] = [df['icd9'][j] for j in df[df['patientunitstayid']==i].index]


# In[ ]:





# In[30]:


#get icd-9 codes for patient i from diagnosis table
# print(d)

import warnings
warnings.filterwarnings("ignore")

create_dict()
fdf = final_dataframe()

patient_id = df["patientunitstayid"]
print(len(patient_id))
con_list = [fdf]
for patient in patient_id:
    icd_list = df.loc[df['patientunitstayid'] == patient, 'icd9'].item()
#     print(icd_list)
#     break
    df_last = elix_score(patient,icd_list)
    con_list.append(df_last)
fdf = pd.concat(con_list)
print(fdf)


# In[31]:


fdf.to_csv("patient_co_morbidity.csv")

print(fdf.shape)


# In[ ]:


# patient_id = [12,14]
# con_list = [fdf]
# for patient in patient_id:
#     icd_list = ['425.5','V45.0','201.3','202.9','203.0']
#     df_last = elix_score(patient,icd_list)
#     con_list.append(df_last)
# fdf = pd.concat(con_list)
# print(fdf)

