import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine
from connection import conn
import streamlit as st
from sqlalchemy import text
from matplotlib.axis import XAxis
from matplotlib.pyplot import title
import pandas as pd
import psycopg2
from pyparsing import White
import sqlalchemy
from sqlalchemy import create_engine
from connection import *
from twitter_metrics import *
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
pio.templates 

def follower_age_category(data):
    import datetime as dt
    data["max_rank"] = data.groupby("username")["computed_date"].rank("dense",ascending=False)
    d_df=data[data['max_rank']==1.0]
    d_df = d_df.drop_duplicates(subset=['username'])

    d_df['created']=pd.to_datetime(d_df['created'])


    d_df['created_date'] = d_df['created'].dt.date

    d_df['diff_days'] = (d_df['computed_date'] - d_df['created_date']).dt.days

    def age_groups(row):
        if row['diff_days'] > 1460:
            return '>4 years'
        elif row['diff_days'] >= 1096 and row['diff_days'] <= 1460:
            return '3 - 4 years'
        elif row['diff_days'] >= 731 and row['diff_days'] <= 1095:
            return '2 - 3 years'
        elif row['diff_days'] >= 366 and row['diff_days'] <= 730:
            return '1 - 2 years'
        elif row['diff_days'] >= 182 and row['diff_days'] <= 365:
            return '6 - 12 months'
        elif row['diff_days'] >= 32 and row['diff_days'] <= 61:
            return '1 - 6 months'
        elif row['diff_days'] >= 11 and row['diff_days'] <= 31:
            return '11 - 30 days'        
        else:
            return '<10 days'
    d_df['age_category'] = d_df.apply(age_groups, axis=1)   


    def followers_category(row):
        if row['followerscount'] > 10000:
            return '> 10000'
        elif row['followerscount'] >= 5001 and row['followerscount'] <= 10000:
            return '5001-10000'
        elif row['followerscount'] >= 1001 and row['followerscount'] <= 5000:
            return '1001-5000'
        elif row['followerscount'] >= 501 and row['followerscount'] <= 1000:
            return '501-1000'
        elif row['followerscount'] >= 101 and row['followerscount'] <= 500:
            return '101-500'    
        elif row['followerscount'] >= 51 and row['followerscount'] <= 100:
            return '51-100' 
        elif row['followerscount'] >= 41 and row['followerscount'] <= 50:
            return '41-50'                         
        elif row['followerscount'] >= 31 and row['followerscount'] <= 40:
            return '31-40'    
        elif row['followerscount'] >= 21 and row['followerscount'] <= 30:
            return '21-30'    
        elif row['followerscount'] >= 10 and row['followerscount'] <= 20:
            return '10-20'                                           

        else:
            return '<10'            
    d_df['followers_category'] = d_df.apply(followers_category, axis=1)           
        
    age_category_data = d_df.groupby('age_category').agg({'id':'count'})
    age_category_data = age_category_data.reset_index()
    age_category_data = age_category_data.rename(columns={'id':'Number of Users'})
    age_category_data = age_category_data.sort_values(by=['age_category'])
    


    follower_category_data = d_df.groupby('followers_category').agg({'id':'count'})
    follower_category_data = follower_category_data.reset_index()
    follower_category_data = follower_category_data.rename(columns={'id':'Number of Users'})
    followers_category_data = follower_category_data.sort_values(by=['followers_category'])
    return age_category_data, follower_category_data       







def tweet_category(data):
    tweet_cat = data.groupby('username').agg({'id':'count'})
    tweet_cat = tweet_cat.reset_index()
    def tweet_range(row):
        if row['id'] > 10:
            return '>10 Tweets'
        elif row['id'] > 5 and row['id'] <= 10:
            return '6-10 Tweets'
        elif row['id'] >= 3 and row['id'] <= 5:
            return '3-5 Tweets'
        elif row['id'] == 2:
            return '2 Tweets'
        else:
            return '1 Tweet'
    tweet_cat['tweet_category'] = tweet_cat.apply(tweet_range, axis=1)        
        
    tweet_category = tweet_cat.groupby('tweet_category').agg({'id':'count'})
    tweet_category = tweet_category.reset_index()

    tweet_category = tweet_category.rename(columns={'id':'Number of Users'})
    tweet_category = tweet_category.sort_values(by=['tweet_category'])
    return tweet_category   



def age_category_plot(data):
        fig = px.bar(data, x = data['age_category'], y = data['Number of Users'], text_auto='.2s',title='Age category Frequency')
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':['<10 days','11 - 30 days','1 - 6 months','6 - 12 months','1 - 2 years','2 - 3 years','3 - 4 years','>4 years']})
        st.plotly_chart(fig,use_container_width = True)    



def followers_category_plot(data):
        fig = px.bar(data, x = data['followers_category'], y = data['Number of Users'], text_auto='.2s',title='Users by Followers range')
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':['<10','10-20','21-30','31-40','41-50','51-100','101-500','501-1000','1001-5000','5001-10000','> 10000']})
        st.plotly_chart(fig,use_container_width = True)           

def tweet_category_plot(data):
        fig = px.bar(data, x = data['tweet_category'], y = data['Number of Users'], text_auto='.2s',title='Tweets Frequency')
        st.plotly_chart(fig,use_container_width = True)         