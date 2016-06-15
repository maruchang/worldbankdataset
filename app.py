import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.ticker import FuncFormatter
import re
matplotlib.style.use('ggplot')
import datetime as dt
from scipy.interpolate import spline
from math import floor

#Find path of the projects csv file
path = os.path.realpath('app.py')
path = path[:-6]

#Parse dates 
dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

#Create projects data frame
df = pd.DataFrame()
df = pd.read_csv(path+str('api.csv'),dtype={'boardapprovaldate': str})
#Drop columns which are all NA
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


########## Lending commitments over time ##########
dfnew1 = dfnew[['year','lendprojectcost','ibrdcommamt','idacommamt']].groupby('year').sum()
dfnew1.columns = ['Total Lending Commitment','IBRD Amount Committed','IDA Amount Committed']

def millions(x, pos):
    'The two args are the value and tick position'
    return '$%1.1fB' % (x*1e-9)
formatter = FuncFormatter(millions)    

ax = dfnew1.plot()
ax.yaxis.set_major_formatter(formatter)
ax.legend(loc='upper left')

########## Lending commitments over time in different regions ##########
region_dict = {0:'r',1:'g',2:'b',3:'c',4:'k',5:'m',6:'y'}
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()

for i,region in enumerate(dfnew.regionname.unique()):
    
    dfnewtemp = pd.DataFrame()
    
    print region
    dfnewtemp = dfnew.loc[df['regionname'] == region,['year','lendprojectcost','ibrdcommamt','idacommamt']]
    dfnewtemp = dfnewtemp.groupby('year').sum()
    
    years = dfnewtemp.index
    lendprojectcost = dfnewtemp.lendprojectcost
    ibrdcommamt = dfnewtemp.ibrdcommamt
    idacommamt = dfnewtemp.idacommamt
    
    xnew = np.linspace(years.min(),years.max(),300)
    

    lendprojectcost_smooth = spline(years,lendprojectcost,xnew)
    ax2.plot(xnew,lendprojectcost_smooth, region_dict[i], label = region)
    
    ibrdcommamt_smooth = spline(years,ibrdcommamt,xnew)
    ax3.plot(xnew,ibrdcommamt_smooth, region_dict[i], label = region)    

    idacommamt_smooth = spline(years,idacommamt,xnew)
    ax4.plot(xnew,idacommamt_smooth, region_dict[i], label = region)    

ax2.yaxis.set_major_formatter(formatter)
ax2.set_xlabel('Years')
ax2.set_ylabel('Total Lending Commitment?')
ax2.legend(loc='upper left')

ax3.yaxis.set_major_formatter(formatter)
ax3.set_xlabel('Years')
ax3.set_ylabel('IBRD Commitment')
ax3.legend(loc='upper left')

ax4.yaxis.set_major_formatter(formatter)
ax4.set_xlabel('Years')
ax4.set_ylabel('IDA Commitment')
ax4.legend(loc='upper left')
    
########## Focus areas sorted by number of projects
dfnew.loc[:,'sector1rmhisttag'] = dfnew.sector1.str.replace('!.*$','',case=False)
dfnew.loc[:,'theme1rmhisttag'] = dfnew.theme1.str.replace('!.*$','',case=False)

def decade(x):
    dec = str(int(floor(x*1.0/5)*5))
    return dec+'-'+str(int(dec[-2:])+4)
getdec = lambda year: decade(year)        
dfnew.loc[:,'dec'] = dfnew.year.apply(getdec)

##########
fig5, ax5 = plt.subplots()
countby_dec_and_s1 = dfnew.groupby(['dec','sector1rmhisttag']).id.count()

g1 = []
g1_val = []
g2 = []
g2_val = []
g3 = []
g3_val = []

for dec in countby_dec_and_s1.index.get_level_values(0).unique():
    temp = countby_dec_and_s1.loc[dec].sort_values(ascending=False).head(3)/ \
            sum(countby_dec_and_s1.loc[dec])*100
    label = []
    for t in temp.index:
        tmp = t.replace('(Historic)','(H)').split()
        tmp = ' '.join(tmp)
        tmp = tmp.replace('administration','admin').split()
        if 'social services' in tmp:
            tmp = 'Other Social'
        label.append(' '.join(tmp))
                
    g1_val.append(temp[0])
    g1.append(label[0])
    g2_val.append(temp[1])
    g2.append(label[1])    
    g3_val.append(temp[2])
    g3.append(label[2])    

N = len(dfnew.dec.unique())
ind = np.arange(N)  # the x locations for the groups
width = 0.25       # the width of the bars

rects1 = ax5.bar(ind, g1_val, width, color='r')
rects2 = ax5.bar(ind + width, g2_val, width, color='b')
rects3 = ax5.bar(ind + width + width, g3_val, width, color='y')

# add some text for labels, title and axes ticks
ax5.set_ylabel('Number of projects')
ax5.set_title('Top 3 sectors in which projects were sanctioned')
ax5.set_xticks(ind + width*3/2)
ax5.set_xticklabels(countby_dec_and_s1.index.get_level_values(0).unique(), rotation = 30)

def autolabel(rects,g,ax):
    for i,rect in enumerate(rects):
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, g[i],
                ha='center', va='bottom', rotation = 90)
                
autolabel(rects1,g1,ax5)
autolabel(rects2,g2,ax5)
autolabel(rects3,g3,ax5)                
ax5.set_ylim([0, 35])

###########
fig6, ax6 = plt.subplots()
dfwiththeme = dfnew[dfnew.boardapprovaldate > dt.datetime(1987,6,25)]
countby_dec_and_t1 = dfwiththeme.groupby(['dec','theme1rmhisttag']).id.count()

g1 = []
g1_val = []
g2 = []
g2_val = []
g3 = []
g3_val = []

for dec in countby_dec_and_t1.index.get_level_values(0).unique():
    if dec == '1985-89':
        temp = countby_dec_and_t1.loc[dec].sort_values(ascending=False)[1:4]/ \
            (sum(countby_dec_and_t1)-\
            countby_dec_and_t1.loc[dec].\
            sort_values(ascending=False)[0])*100
    else:
        temp = countby_dec_and_t1.loc[dec].sort_values(ascending=False).head(3)/ \
            sum(countby_dec_and_t1)*100        
    print temp
    label = []
    for t in temp.index:
        tmp = t.replace('(Historic)','(H)').split()
        tmp = ' '.join(tmp)
        tmp = tmp.replace('administration','admin').split()
        if 'social services' in tmp:
            tmp = 'Other Social'
        label.append(' '.join(tmp))
        
    g1_val.append(temp[0])
    g1.append(label[0])
    g2_val.append(temp[1])
    g2.append(label[1])    
    g3_val.append(temp[2])
    g3.append(label[2])    

N = len(dfwiththeme.dec.unique())
ind = np.arange(N)  # the x locations for the groups
width = 0.25       # the width of the bars

rects1 = ax6.bar(ind, g1_val, width, color='r')
rects2 = ax6.bar(ind + width, g2_val, width, color='b')
rects3 = ax6.bar(ind + width + width, g3_val, width, color='y')

# add some text for labels, title and axes ticks
ax6.set_ylabel('Number of projects')
ax6.set_title('Top 3 themes for sanctioned projects')
ax6.set_xticks(ind + width*3/2)
ax6.set_xticklabels(countby_dec_and_t1.index.get_level_values(0).unique(), rotation = 30)
ax6.set_ylim([0, 10])
          
autolabel(rects1,g1,ax6)
autolabel(rects2,g2,ax6)
autolabel(rects3,g3,ax6)                

plt.show()