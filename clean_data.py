import pandas as pd
import time
from datetime import datetime, timedelta, date, time
import pytz
from pytz import timezone
import scraper


df = pd.read_csv('uncleaned_data.csv')

#REMOVE WHITESPACE

df['test_info'] = df['test_info'].str.replace(r'\n', '')
df['ID'] = df['ID'].str.replace(r'\n', '')
df['ID'] = df['ID'].str.replace(r'View details', '')
df['payment_status'] = df['payment_status'].str.replace(r'\n', '')
df['rating'] = df['rating'].str.replace(r'\n', '')


#REMOVE NULL ROWS

df.isnull().values.any()
nan_rows = df[df.isnull().T.any()]
df = df.drop(index = nan_rows.index.values)

#reset indices 
df.reset_index(drop=True, inplace=True)


#CREATE DATE, TIME, AND DAY OF WEEK COLUMNS 

#extract date and time columns
df['date'] = df['test_info'].str[:10]
df['time'] = df['test_info'].str[11:]
df['time'] = df['time'].str.replace(r'PST', '')
df['time'] = df['time'].str.replace(r'PDT', '')
df['time'] = df['time'].str[:-1]

#convert to columns to datetime type
df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%m/%d/%Y')
df['time'] = pd.to_datetime(df['time'], errors='coerce', format="%I:%M %p") + timedelta(hours=3) #Eastern Standard Time Conversion
df['time'] = df['time'].dt.time

#remove NAT values in Date column 
df = df.drop(index = df[df.date.isnull()].index.values) 

#reset indices 
df.reset_index(drop=True, inplace=True)

#add day of week column
df['day_of_week'] = df['date'].apply(lambda x: x.strftime('%A'))



#isolate compensation function
def comp(row):
    if row['payment_status'] == '' or row['payment_status'] == 'None':
        val = 0
    elif '10.00' in row['payment_status']:
        val = 10
    elif '4.00' in row['payment_status']:
        val = 4
    return val

df['comp'] = df.apply(comp, axis=1)
df['comp'] = df['comp'].astype(int)


#CLEAN RATING COLUMN

for i in range(len(df.index.values)):
    if ('stars' in df['rating'][i]) and (len(df['rating'][i]) > 16):
        df['rating'][i] = df['rating'][i][:16]


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


#ADD TIME OF DAY COLUMN
tod = []
for i in range(len(df.index.values)):
    if(time_in_range(time(5, 0), time(9, 59),df['time'][i])):
        tod.append('Morning')
    elif(time_in_range(time(10, 0), time(13, 59),df['time'][i])):
        tod.append('Late Morning')
    elif(time_in_range(time(14, 0), time(19, 59),df['time'][i])):
        tod.append('Afternoon')
    else:
        tod.append('Night')
tod

df['day_quarter'] = tod


#DROP UNECESSARY COLUMNS

df = df.drop('payment_status', axis=1)
df = df.drop('test_info', axis=1)


#SAVE DATAFRAME TO CSV 
    
df.to_csv(r'cleaned_data.csv', index=False)

