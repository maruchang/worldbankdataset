import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import datetime as dt

path = os.path.realpath('app.py')
path = path[:-6]


dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

df = pd.DataFrame()
df = pd.read_csv(path+str('api.csv'),dtype={'boardapprovaldate': str})
df.dropna(axis=1,how='all',inplace=True)

def convert_date(val):
    try:
        y,m,d = val.split('-')
        d = d[:2]
    except AttributeError:
        return pd.NaT
    return dt.datetime(int(y),int(m),int(d))

def convert_money(val):
    if val == '0':
        return int(0)
    try:
        b = val.split(';')
        i = 0
        sums = 0
        for n in reversed(b):
            sums += int(n)*(1000**(i))
            i+=1
        return int(sums)
    except AttributeError:
        return np.NaN
        
            
df.boardapprovaldate = df.boardapprovaldate.map(convert_date)
df.closingdate = df.closingdate.map(convert_date)
df.lendprojectcost = df.lendprojectcost.map(convert_money)
df.ibrdcommamt = df.ibrdcommamt.map(convert_money)
df.idacommamt = df.idacommamt.map(convert_money)
df.totalamt = df.totalamt.map(convert_money)
df.grantamt = df.grantamt.map(convert_money)


dfnew = pd.DataFrame()
dfnew = df[(df.boardapprovaldate.notnull()) & \
          (df.lendprojectcost.notnull())]
dfnew.loc[:,'year'] = dfnew.boardapprovaldate.apply(lambda x: x.year)   



dfnew1 = dfnew[['year','lendprojectcost','ibrdcommamt','idacommamt']].groupby('year').sum()
dfnew1.columns = ['Total Lending Commitment','IBRD Amount Committed','IDA Amount Committed']
dfnew1.plot()



for region in dfnew.regionname.unique():
    dfnewtemp = pd.DataFrame()
    print region
    dfnewtemp = dfnew.loc[df['regionname'] == region,['year','ibrdcommamt','idacommamt']]
    dfnewtemp = dfnewtemp.groupby('year').sum()
    dfnewtemp.plot.bar(title=region)
