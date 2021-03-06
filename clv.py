# -*- coding: utf-8 -*-
"""Customer Lifetime Value Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y6VxZ__aNKB5mDpH4EdLxJyCJUGdbpV8
"""

!pip install lifetimes

import pandas as pd
import matplotlib.pyplot as plt

data=pd.read_csv('/content/drive/MyDrive/Online Retail.csv')

data.head()

data.shape

data.isnull().sum()

data.columns

data['InvoiceDate']=pd.to_datetime(data['InvoiceDate'],format='%m/%d/%y %H:%M').dt.date

data=data[pd.notnull(data['CustomerID'])]

data=data[data['Quantity']>0]

data

data['Total']=data['Quantity']*data['UnitPrice']

cols=['CustomerID','InvoiceDate','Total']

data=data[cols]

data.head()

data['CustomerID'].nunique()

last_order_date=data['InvoiceDate'].max()

last_order_date

from lifetimes.utils import summary_data_from_transaction_data

df=summary_data_from_transaction_data(data,'CustomerID','InvoiceDate',monetary_value_col='Total',observation_period_end=last_order_date)

df.reset_index().head()

fig=plt.figure(figsize=(20,10))
df['frequency'].plot(kind='hist',bins=20)

df['frequency'].describe()

one_time=round(sum(df['frequency']==0)/float(len(df))*100,2)

print("Percentage of one time customers is",one_time,"%")

"""**Frequency and Recency Analysis | BG/NBD Model**"""

from lifetimes import BetaGeoFitter

# similar API to scikit-learn and lifelines.
bgf = BetaGeoFitter(penalizer_coef=0.0)
bgf.fit(df['frequency'], df['recency'], df['T'])
print(bgf)

bgf.summary

from lifetimes.plotting import plot_frequency_recency_matrix
fig=plt.figure(figsize=(20,10))
plot_frequency_recency_matrix(bgf)

#Prediction for Active Customers
from lifetimes.plotting import plot_probability_alive_matrix
fig=plt.figure(figsize=(20,10))
plot_frequency_recency_matrix(bgf)

t=20
df['transaction']=round(bgf.conditional_expected_number_of_purchases_up_to_time(t,df['frequency'],df['recency'],df['T']),2)
df.sort_values('transaction',ascending=False).head(20).reset_index()

from lifetimes.plotting import plot_period_transactions

plot_period_transactions(bgf)

#Individual customer Future Prediction for next 20 days
t=20
Individual=df.iloc[1510]
bgf.predict(t,Individual['frequency'],Individual['recency'],Individual['T'])

df[['monetary_value','frequency']].corr()

import seaborn as sns

fig=plt.figure(figsize=(20,10))
sns.heatmap(df[['monetary_value','frequency']])

# Customers with atleast one repeat purchase
shortlisted=df[df['frequency']>0]

len(shortlisted)

shortlisted.head().reset_index()

"""**GAMMA-GAMMA Model**"""

from lifetimes import GammaGammaFitter
ggf=GammaGammaFitter(penalizer_coef=0)
ggf.fit(shortlisted['frequency'],shortlisted['monetary_value'])

ggf

ggf.conditional_expected_average_profit(df['frequency'],df['monetary_value']).head()

df['transaction_value']=round(ggf.conditional_expected_average_profit(df['frequency'],df['monetary_value']),2)
df.reset_index().head()

df['CLV']=round(ggf.customer_lifetime_value(bgf,df['frequency'],df['recency'],df['T'],df['monetary_value'],time=12,discount_rate=0.01),2)

df.sort_values(by='CLV',ascending=False).reset_index()