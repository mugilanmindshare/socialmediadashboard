import matplotlib.pyplot as plt
import ast
from matplotlib.pyplot import title
import streamlit as st
from streamlit_option_menu import option_menu
import wordcloud
import pandas as pd
import psycopg2
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sqlalchemy
import sys
from sqlalchemy import create_engine
from connection import *
from twitter_metrics import *
from twitter_metrics_graphs import *
import plotly.express as px
from streamlit_card import card
from sentiment import *
from twitter_sentiment_graphs import *
from hashtag_data import *
from wordcloud import WordCloud
from wordcloud_data_graph import *
from datetime import date
from plotly import graph_objs as go
from datetime import datetime
from hashtag_mentions_plots import *
from leader_performance_plots import *
import datetime
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import streamlit_authenticator as stauth
from twitter_mentions_data import *
from twitter_mentions_plots import *
from mentions_sentiment import *
from age_followers_tweet_cat import *
import hydralit_components as hc


#make it look nice from the start
st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

# specify the primary menu definition   <i class="fa-brands fa-twitter-square"></i>
menu_data = [
    {'icon': "fab fa-twitter", 'label':"Twitter", 'submenu':[{'id':'subid11', 'label':"Leaders Activities"},{'id':'subid12', 'label':"Mentions Analysis"}]},
    {"id" : "subidf",'icon': "fab fa-facebook-square", 'label':"facebook"},#no tooltip message
    {'id' : 'subidi','icon': "fab fa-instagram", 'label':"Instagram"},
]

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Home',
    hide_streamlit_markers=True, #will show the st hamburger as well as the navbar now!
    sticky_nav=True, #at the top or not
    sticky_mode='not-jumpy', #jumpy or not-jumpy, but sticky or pinned
)
selected_subpage = menu_id

connection = conn()

data = pd.read_sql_table('social_media_dashboard_login_authentication', connection)

username = data['username'].tolist()
password = data['password'].tolist()
name=[1,2]

authenticator = stauth.Authenticate(name,username,password,'sm_authenticator', 'abcdef', cookie_expiry_days = 30)

name,authentication_status,username = authenticator.login('Login','sidebar')

st.markdown("""<style>div[data-testid="metric-container"] {background-color: rgba(28, 131, 225, 0.1);border: 1px solid rgba(28, 131, 225, 0.1);padding: 5% 5% 5% 10%;border-radius: 5px;color: rgb(30, 103, 119);overflow-wrap: break-word;}div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {overflow-wrap: break-word;white-space: break-spaces;color: red;}</style>""", unsafe_allow_html=True)

if authentication_status == 'False':
    if selected_subpage == 'Home':
        st.warning('Wrong Username/Password')    
    if selected_subpage == 'subid11':
        st.error('Please login to access this page')
    if selected_subpage == 'subid12':
        st.error('Please login to access this page')        
    if selected_subpage == 'subidf':
        st.error('Please login to access this page')
    if selected_subpage == 'subidi':
        st.error('Please login to access this page')          
if authentication_status == None:
    if selected_subpage == 'Home':
        st.warning('Please login to access this page')
    if selected_subpage == 'subid11':
        st.error('Please login to access this page')
    if selected_subpage == 'subid12':
        st.error('Please login to access this page')  
    if selected_subpage == 'subidf':
        st.error('Please login to access this page')
    if selected_subpage == 'subidi':
        st.error('Please login to access this page')            
if authentication_status == True:
    authenticator.logout('Logout','sidebar')
    
    if selected_subpage == 'subid11':
        st. markdown("<h1 style='text-align: center; color: red;'>Leaders Activities</h1>", unsafe_allow_html=True)
        con=conn()
        leader_ul_data = over_all_twitter_metrics()

        search_col,from_col,to_col=st.columns((3,2,2))
        with search_col:
            add_selectbox = st.multiselect("Please Select Leader",leader_ul_data['username'].unique(),default=None)
        with from_col:
            from_date=st.date_input('From Date', value = None, min_value = datetime.date(2019, 1, 1), max_value = date.today())
        with to_col:
            to_date=st.date_input('To Date', value=None, min_value = datetime.date(2019, 1, 1), max_value = date.today())    


        
        from datetime import datetime
        selected_leader_ul_data = leader_ul_data[leader_ul_data['username'].isin(add_selectbox)]
        selected_leader_ul_data['computed_date'] = pd.to_datetime(selected_leader_ul_data['computed_date'], format='%Y-%m-%d')
        selected_leader_ul_data['week'] = selected_leader_ul_data['computed_date'].dt.week
        selected_leader_ul_data = selected_leader_ul_data[(selected_leader_ul_data['computed_date'] >= pd.to_datetime(str(from_date), format='%Y-%m-%d')) & (selected_leader_ul_data['computed_date'] <= pd.to_datetime(str(to_date), format='%Y-%m-%d'))]
        leader_ul_overall_sentiment = over_all_sentiment(selected_leader_ul_data)
        #tiles()
        year_data = year_wise_twitter_metrics(selected_leader_ul_data)


        month_data = month_year_wise_twitter_metrics(selected_leader_ul_data)


        week_data = week_wise_twitter_metrics(selected_leader_ul_data)

        day_data = day_wise_twitter_metrics(selected_leader_ul_data)


        hour_data = hour_wise_twitter_metrics(selected_leader_ul_data)






        selected_wordcloud_data = selected_leader_ul_data.copy()
        selected_overall_wordcloud_data = selected_wordcloud_data[['username','tweets_no_stopwords']]
        selected_positive_wordcloud_data = selected_wordcloud_data[selected_wordcloud_data['vader_sentiment'] == 'Positive']
        selected_negative_wordcloud_data = selected_wordcloud_data[selected_wordcloud_data['vader_sentiment'] == 'Negative'] 
        selected_neutral_wordcloud_data = selected_wordcloud_data[selected_wordcloud_data['vader_sentiment'] == 'Neutral']
        overall_hashtag = selected_wordcloud_data[['username','hashtag']]


        selected_diff = pd.to_datetime(str(to_date), format='%Y-%m-%d') - pd.to_datetime(str(from_date), format='%Y-%m-%d')
        selected_day_diff = selected_diff.days

        if selected_day_diff > 730:
            c1,c2 = st.columns((5,1))
            with c1:
                level = st.radio("Please select Level for Graph",('Hour','Day','Week','Month','Year'),key='123')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
            with c2:
                total_tweet = hour_data['total_tweets'].tolist()
                st.metric('Total Tweets',sum(total_tweet),delta = None)
        elif selected_day_diff > 60:
            c1,c2 = st.columns((5,1))
            with c1:
                level = st.radio("Please select Level for Graph",('Hour','Day','Week','Month'),key='4')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
            with c2:
                total_tweet = hour_data['total_tweets'].tolist()
                st.metric('Total Tweets',sum(total_tweet),delta = None)    
        elif selected_day_diff > 14:
            c1,c2 = st.columns((5,1))
            with c1:
                level = st.radio("Please select Level for Graph",('Hour','Day','Week'),key=5)
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
            with c2:
                total_tweet = hour_data['total_tweets'].tolist()
                st.metric('Total Tweets',sum(total_tweet),delta = None)    
        elif selected_day_diff > 1:
            c1,c2 = st.columns((5,1))
            with c1:
                level = st.radio("Please select Level for Graph",('Hour','Day'),key=6)
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
            with c2:
                total_tweet = hour_data['total_tweets'].tolist()
                st.metric('Total Tweets',sum(total_tweet),delta = None)    
        else:
            c1,c2 = st.columns((5,1))
            with c1:
                level = st.radio("Please select Level for Graph",(['Hour']),key=7)
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
            with c2:
                total_tweet = hour_data['total_tweets'].tolist()  
                #theme_neutral = {'bgcolor': '#fcf8e5','title_color': 'black','content_color': 'black'}
                #hc.info_card(title="Total Tweets",title_text_size='1rem', content=sum(total_tweet), icon_size='0rem',sentiment='good',bar_value=0,theme_override=theme_neutral)
            
                st.metric('Total Tweets',sum(total_tweet),delta = None)
            
                

        if level == 'Year':
            col1,col2=st.columns((3,3))
            with col1:
                year_wise_total_tweets_plot(year_data)
            with col2:
                year_wise_total_likes_plot(year_data)
            col111,col222=st.columns((3,3))
            with col111:
                year_wise_total_replies_plot(year_data)
            with col222:
                year_wise_total_retweets_plot(year_data)    
            col11,col12=st.columns((3,3))
            with col11:   
                year_wise_total_quotes_plot(year_data)
            with col12:
                if len(selected_leader_ul_data) > 0:            
                    fig = px.bar(leader_ul_overall_sentiment, x = leader_ul_overall_sentiment['vader_sentiment'], y = leader_ul_overall_sentiment['id'], color = leader_ul_overall_sentiment['username'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)  

        elif level == 'Month':
            m1,m2=st.columns((3,3))
            with m1:
                month_wise_total_tweets_plot(month_data)
            with m2:
                month_wise_total_likes_plot(month_data)
            m3,m4=st.columns((3,3))
            with m3:   
                month_wise_total_replies_plot(month_data)
            with m4:
                month_wise_total_retweets_plot(month_data)
            m5,m6=st.columns((3,3))
            with m5:
                month_wise_total_quotes_plot(month_data)
            with m6:
                if len(selected_leader_ul_data) > 0:            
                    fig = px.bar(leader_ul_overall_sentiment, x = leader_ul_overall_sentiment['vader_sentiment'], y = leader_ul_overall_sentiment['id'], color = leader_ul_overall_sentiment['username'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)    

        elif level == 'Week':
            w1,w2=st.columns((3,3))
            with w1:
                week_wise_total_tweets_plot(week_data)
            with w2:
                week_wise_total_likes_plot(week_data)    
            w3,w4 = st.columns((3,3))
            with w3:
                week_wise_total_replies_plot(week_data)
            with w4:
                week_wise_total_retweets_plot(week_data)  
            w5,w6=st.columns((3,3))
            with w5:
                week_wise_total_quotes_plot(week_data)
            with w6:
                if len(selected_leader_ul_data) > 0:            
                    fig = px.bar(leader_ul_overall_sentiment, x = leader_ul_overall_sentiment['vader_sentiment'], y = leader_ul_overall_sentiment['id'], color = leader_ul_overall_sentiment['username'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)           


        elif level == 'Day':
            d1, d2 = st.columns((3,3))
            with d1:
                day_wise_total_tweets_plot(day_data)
            with d2:
                day_wise_total_likes_plot(day_data)
            d3,d4 = st.columns((3,3))
            with d3:
                day_wise_total_replies_plot(day_data)
            with d4:
                day_wise_total_retweets_plot(day_data)
            d5, d6 = st.columns ((3,3))
            with d5:
                day_wise_total_quotes_plot(day_data)  
            with d6:
                if len(selected_leader_ul_data) > 0:            
                    fig = px.bar(leader_ul_overall_sentiment, x = leader_ul_overall_sentiment['vader_sentiment'], y = leader_ul_overall_sentiment['id'], color = leader_ul_overall_sentiment['username'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)            
        else:
            h1, h2 = st.columns((3,3))
            with h1:
                hour_wise_total_tweets_plot(hour_data)
            with h2:
                hour_wise_total_likes_plot(hour_data)
            h3, h4 = st.columns((3,3))
            with h3:
                hour_wise_total_replies_plot(hour_data)
            with h4:
                hour_wise_total_retweets_plot(hour_data)
            h5, h6 = st.columns((3,3))
            with h5:
                hour_wise_total_quotes_plot(hour_data)    
            with h6:
                if len(selected_leader_ul_data) > 0:
                    fig = px.bar(leader_ul_overall_sentiment, x = leader_ul_overall_sentiment['vader_sentiment'], y = leader_ul_overall_sentiment['id'], color = leader_ul_overall_sentiment['username'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)        




        hashtagg_data = find_hashtag_fre(selected_leader_ul_data)
        hashtagg_category_data = hastags_category_fun(hashtagg_data)

        mensions_data = find_mentions_fre(selected_wordcloud_data)
        mensions_category_data = mentions_category_fun(mensions_data)


        over_all_wordcloud_expander = st.expander(label='Overall WordCloud')
        with over_all_wordcloud_expander:
            ex_col1,ex_col2 = st.columns((3,3)) 
            with ex_col1:
                if len(selected_leader_ul_data) > 0:
                    overall_wordcloud(selected_wordcloud_data['tweets_no_stopwords'])
            with ex_col2:
                overall_hashtag_plot(hashtagg_category_data)
            overall_mentions_plot(mensions_category_data)        


        posword_col,negword_col,neuword_col = st.columns((1,1,1))
        with posword_col:
            positive_wordcloud_expander = st.expander(label='Positive WordCloud')
            with positive_wordcloud_expander:
                if len(selected_leader_ul_data) > 0 and len(selected_positive_wordcloud_data['tweets_no_stopwords']) > 0:
                    positive_wordcloud(selected_positive_wordcloud_data['tweets_no_stopwords'])
        with negword_col:
            negative_wordcloud_expander = st.expander(label='Negative WordCloud')
            with negative_wordcloud_expander:
                if len(selected_leader_ul_data) > 0 and len(selected_negative_wordcloud_data['tweets_no_stopwords']) > 0:
                    negative_wordcloud(selected_negative_wordcloud_data['tweets_no_stopwords'])
        with neuword_col:
            neutral_wordcloud_expander = st.expander(label='Neutral WordCloud')
            with neutral_wordcloud_expander:
                if len(selected_leader_ul_data) > 0 and len(selected_neutral_wordcloud_data['tweets_no_stopwords']) > 0:                
                    neutral_wordcloud(selected_neutral_wordcloud_data['tweets_no_stopwords'])






        hashtag_analysis_expander = st.expander(label='Hashtag Analysis')
        with hashtag_analysis_expander:
            hashtag_col1,hashtag_col2 = st.columns(2)
            with hashtag_col1:
                uni_hashtag_plot(hashtagg_category_data)
            with hashtag_col2:
                bi_hashtag_plot(hashtagg_category_data)
            

            hashtag_col3,hashtag_col4 = st.columns(2)
            with hashtag_col3:
                tri_hashtag_plot(hashtagg_category_data)        
            with hashtag_col4:
                multi_hashtag_plot(hashtagg_category_data)






        mentions_analysis_expander = st.expander(label='Mentions Analysis')
        with mentions_analysis_expander:
            mentions_col1,mentions_col2 = st.columns(2)
            with mentions_col1:
                uni_mentions_plot(mensions_category_data)
            with mentions_col2:
                bi_mentions_plot(mensions_category_data)
            tri_mentions_plot(mensions_category_data)        

            multi_mentions_plot(mensions_category_data)



        leaders_performance_data = leaders_overall_performance(leader_ul_data)
        leaders_performance_data = leaders_performance_data[(leaders_performance_data['username']).isin(add_selectbox)]
        leader_overall_performance_radar_chart(leaders_performance_data)

        selected_leaders_performance_data = leaders_overall_performance(selected_leader_ul_data)

        leader_overall_performance_radar_chart_selected_time_range(selected_leaders_performance_data)

        
        
        gb = GridOptionsBuilder.from_dataframe(selected_leader_ul_data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            selected_leader_ul_data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='blue', #Add theme color to the table
            enable_enterprise_modules=True,
            height=350, 
            width='100%',
            reload_data=True
        )





    elif selected_subpage == 'subid12':
        st. markdown("<h1 style='text-align: center; color: red;'>Mentions Analysis</h1>", unsafe_allow_html=True)
        con=conn()
        #search_list = get_username_for_search()
        
        #st.write(leader_ul_data)
        from datetime import date 
        mentions_search_col,mentions_from_col,mentions_to_col = st.columns((3,2,2))
        with mentions_search_col:
            mentions_add_selectbox = st.multiselect("Please Select Leader", ['ncbn','naralokesh','ysjagan','PawanKalyan','TelanganaCMO','KTRTRS','bandisanjay_bjp','TigerRajaSingh','imAkbarOwaisi','asadowaisi','revanth_anumula','Arvindharmapuri','BSBommai','BSYBJP','siddaramaiah','DKShivakumar','hd_kumaraswamy','H_D_Devegowda','narendramodi','rahulgandhi','ArvindKejriwal','MamataOfficial','PawarSpeaks','ComradeDRaja','SitaramYechury','Mayawati','yadavtejashwi','SangmaConrad','priyankagandhi','ShashiTharoor','AmitShah','msisodia','myogiadityanath'], default=None)
        with mentions_from_col:
            mentions_from_date = st.date_input('Start Date', value = None, min_value = date(2019, 1, 1), max_value = date.today())
        with mentions_to_col:
            mentions_to_date = st.date_input('End Date', value = None, min_value = date(2019, 1, 1), max_value = date.today())    

        #leader_ul_data 


        mentions_overall_data = over_all_twitter_mentions_data(mentions_add_selectbox,mentions_from_date,mentions_to_date)

        twitter_mentions_year_data = year_wise_twitter_mention_metrics(mentions_overall_data)

        twitter_mentions_month_year_data = month_year_wise_twitter_mention_mentions(mentions_overall_data)

        mentions_overall_data['computed_date_time'] = pd.to_datetime(mentions_overall_data['computed_date'].astype('str') + ' ' + mentions_overall_data['computed_time'].astype('str'))
        mentions_overall_data['week'] = mentions_overall_data['computed_date_time'].dt.week

        twitter_mentions_week_data = week_wise_twitter_mention_mentions(mentions_overall_data)

        twitter_mentions_day_data = day_wise_twitter_mention_mentions(mentions_overall_data)


        twitter_mentions_hour_data = hour_wise_twitter_mention_mentions(mentions_overall_data)

        leader_mentions_overall_sentiment = mentions_over_all_sentiment(mentions_overall_data)


        selected_mentions_wordcloud_data = mentions_overall_data.copy()
        selected_mentions_overall_wordcloud_data = selected_mentions_wordcloud_data[['mentioned_user','tweets_no_stopwords']]
        selected_mentions_positive_wordcloud_data = selected_mentions_wordcloud_data[selected_mentions_wordcloud_data['vader_sentiment'] == 'Positive']
        selected_mentions_negative_wordcloud_data = selected_mentions_wordcloud_data[selected_mentions_wordcloud_data['vader_sentiment'] == 'Negative'] 
        selected_mentions_neutral_wordcloud_data = selected_mentions_wordcloud_data[selected_mentions_wordcloud_data['vader_sentiment'] == 'Neutral']
        overall_mentions_hashtag = selected_mentions_wordcloud_data[['mentioned_user','hashtag']]

        selected_mentions_diff = pd.to_datetime(str(mentions_to_date), format='%Y-%m-%d') - pd.to_datetime(str(mentions_from_date), format='%Y-%m-%d')
        selected_mentions_day_diff = selected_mentions_diff.days

        no_unique_users = len(mentions_overall_data['username'].unique().tolist())
        v_vs_unv = mentions_overall_data.groupby('username').agg({'id':'max'})
        v_vs_unv = v_vs_unv.reset_index()
        verified_vs_unverified = pd.merge(v_vs_unv, mentions_overall_data, on='id', how='left')
        verified_vs_unverified = verified_vs_unverified.drop_duplicates(subset=['username_x'])
        verified_vs_unverified = verified_vs_unverified.replace('False','false')
        verified_vs_unverified = verified_vs_unverified.groupby('verified').agg({'username_x':'count'})
        verified_vs_unverified = verified_vs_unverified.reset_index()

        mc1,mc2,mc3,mc4,mc5 = st.columns((2,2,2,2,2))
        with mc1:
            st.metric('No of Unique Users',no_unique_users,delta=None)
        with mc2:
            mentions_total_tweet = twitter_mentions_hour_data['total_tweets'].tolist()
            st.metric('Total Tweets',sum(mentions_total_tweet),delta = None)            
        with mc3:
            st.metric('Total No of Positive Tweets',len(selected_mentions_positive_wordcloud_data),delta=None)            
        with mc4:
            st.metric('Total No of Negative Tweets',len(selected_mentions_negative_wordcloud_data),delta=None)            
        with mc5:         
            st.metric('Total No of Neutral Tweets',len(selected_mentions_neutral_wordcloud_data),delta=None)
            
        m_g_c1,m_g_c2,m_g_c3 = st.columns((2,2,2))
        with m_g_c1:    
            fig = px.bar(verified_vs_unverified, y='username_x', x='verified', text_auto='.2s', orientation='v',title='Verified Vs Unverified Users').update_layout(yaxis_title="Count")
            fig.update_layout(yaxis = dict(tickfont = dict(size=8)))
            st.plotly_chart(fig,use_container_width = True) 
        if len(mentions_overall_data) > 0:
            age_category_df, follower_category_df = follower_age_category(mentions_overall_data)
        with m_g_c2:
            if len(mentions_overall_data) > 0:    
                age_category_plot(age_category_df)
        with m_g_c3:        
            if len(mentions_overall_data) > 0:    
                followers_category_plot(follower_category_df)            
        m_g_c4,m_g_c5,m_g_c6 = st.columns((2,2,2))   
        with m_g_c4:
            if len(mentions_overall_data) > 0:
                tweet_category_df = tweet_category(mentions_overall_data)
                tweet_category_plot(tweet_category_df)



        if selected_mentions_day_diff > 730:
            m_c1,m_c2 = st.columns((5,1))
            with m_c1:
                mentions_level = st.radio("Please select Level for Graph",('Hour','Day','Week','Month','Year'),key='a')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)

        elif selected_mentions_day_diff > 60:
            m_c1,m_c2 = st.columns((5,1))
            with m_c1:
                mentions_level = st.radio("Please select Level for Graph",('Hour','Day','Week','Month'),key='b')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
   
        elif selected_mentions_day_diff > 14:
            m_c1,m_c2 = st.columns((5,1))
            with m_c1:
                mentions_level = st.radio("Please select Level for Graph",('Hour','Day','Week'),key='c')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
    
        elif selected_mentions_day_diff > 1:
            m_c1,m_c2 = st.columns((5,1))
            with m_c1:
                mentions_level = st.radio("Please select Level for Graph",('Hour','Day'),key='d')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)
    
        else:
            m_c1,m_c2 = st.columns((5,1))
            with m_c1:
                mentions_level = st.radio("Please select Mentions Level for Graph",(['Hour']),key='unique123')
                st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>',unsafe_allow_html=True)

        if mentions_level == 'Year':
            m_col1,m_col2=st.columns((3,3))
            with m_col1:
                mentions_year_wise_total_tweets_plot(twitter_mentions_year_data)
            with m_col2:
                mentions_year_wise_total_likes_plot(twitter_mentions_year_data)
            m_col111,m_col222=st.columns((3,3))
            with m_col111:
                mentions_year_wise_total_replies_plot(twitter_mentions_year_data)
            with m_col222:
                mentions_year_wise_total_retweets_plot(twitter_mentions_year_data)    
            m_col11,m_col12=st.columns((3,3))
            with m_col11:   
                mentions_year_wise_total_quotes_plot(twitter_mentions_year_data)
            with m_col12:
                if len(mentions_overall_data) != 0:
                    fig = px.bar(leader_mentions_overall_sentiment, x = leader_mentions_overall_sentiment['vader_sentiment'], y = leader_mentions_overall_sentiment['id'], color = leader_mentions_overall_sentiment['mentioned_user'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)  

        elif mentions_level == 'Month':
            m_m1,m_m2=st.columns((3,3))
            with m_m1:
                mentions_month_wise_total_tweets_plot(twitter_mentions_month_year_data)
            with m_m2:
                mentions_month_wise_total_likes_plot(twitter_mentions_month_year_data)
            m_m3,m_m4=st.columns((3,3))
            with m_m3:   
                mentions_month_wise_total_replies_plot(twitter_mentions_month_year_data)
            with m_m4:
                mentions_month_wise_total_retweets_plot(twitter_mentions_month_year_data)
            m_m5,m_m6=st.columns((3,3))
            with m_m5:
                mentions_month_wise_total_quotes_plot(twitter_mentions_month_year_data)
            with m_m6:
                if len(mentions_overall_data) != 0:            
                    fig = px.bar(leader_mentions_overall_sentiment, x = leader_mentions_overall_sentiment['vader_sentiment'], y = leader_mentions_overall_sentiment['id'], color = leader_mentions_overall_sentiment['mentioned_user'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True) 

        elif mentions_level == 'Week':
            m_w1,m_w2=st.columns((3,3))
            with m_w1:
                mentions_week_wise_total_tweets_plot(twitter_mentions_week_data)
            with m_w2:
                mentions_week_wise_total_likes_plot(twitter_mentions_week_data)    
            m_w3,m_w4 = st.columns((3,3))
            with m_w3:
                mentions_week_wise_total_replies_plot(twitter_mentions_week_data)
            with m_w4:
                mentions_week_wise_total_retweets_plot(twitter_mentions_week_data)  
            m_w5,m_w6=st.columns((3,3))
            with m_w5:
                mentions_week_wise_total_quotes_plot(twitter_mentions_week_data)
            with m_w6:
                if len(mentions_overall_data) != 0:            
                    fig = px.bar(leader_mentions_overall_sentiment, x = leader_mentions_overall_sentiment['vader_sentiment'], y = leader_mentions_overall_sentiment['id'], color = leader_mentions_overall_sentiment['mentioned_user'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)    


        elif mentions_level == 'Day':
            m_d1, m_d2 = st.columns((3,3))
            with m_d1:
                mentions_day_wise_total_tweets_plot(twitter_mentions_day_data)
            with m_d2:
                mentions_day_wise_total_likes_plot(twitter_mentions_day_data)
            m_d3,m_d4 = st.columns((3,3))
            with m_d3:
                mentions_day_wise_total_replies_plot(twitter_mentions_day_data)
            with m_d4:
                mentions_day_wise_total_retweets_plot(twitter_mentions_day_data)
            m_d5, m_d6 = st.columns ((3,3))
            with m_d5:
                mentions_day_wise_total_quotes_plot(twitter_mentions_day_data)  
            with m_d6:
                if len(mentions_overall_data) != 0:            
                    fig = px.bar(leader_mentions_overall_sentiment, x = leader_mentions_overall_sentiment['vader_sentiment'], y = leader_mentions_overall_sentiment['id'], color = leader_mentions_overall_sentiment['mentioned_user'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True)           
        else:
            m_h1, m_h2 = st.columns((3,3))
            with m_h1:
                mentions_hour_wise_total_tweets_plot(twitter_mentions_hour_data)
            with m_h2:
                mentions_hour_wise_total_likes_plot(twitter_mentions_hour_data)
            m_h3, m_h4 = st.columns((3,3))
            with m_h3:
                mentions_hour_wise_total_replies_plot(twitter_mentions_hour_data)
            with m_h4:
                mentions_hour_wise_total_retweets_plot(twitter_mentions_hour_data)
            m_h5, m_h6 = st.columns((3,3))
            with m_h5:
                mentions_hour_wise_total_quotes_plot(twitter_mentions_hour_data)    
            with m_h6:
                if len(mentions_overall_data) != 0:            
                    fig = px.bar(leader_mentions_overall_sentiment, x = leader_mentions_overall_sentiment['vader_sentiment'], y = leader_mentions_overall_sentiment['id'], color = leader_mentions_overall_sentiment['mentioned_user'],title='Overall Sentiment Frequency')
                    st.plotly_chart(fig,use_container_width = True) 




        m_hashtagg_data = m_find_hashtag_fre(mentions_overall_data)
        m_hashtagg_category_data = m_hastags_category_fun(m_hashtagg_data)

        m_mensions_data = m_find_mentions_fre(mentions_overall_data)
        m_mensions_category_data = m_mentions_category_fun(m_mensions_data)


        m_over_all_wordcloud_expander = st.expander(label='Overall WordCloud')
        with m_over_all_wordcloud_expander:
            m_ex_col1,m_ex_col2 = st.columns((3,3)) 
            with m_ex_col1:
                if len(selected_mentions_wordcloud_data['tweets_no_stopwords']) > 0:
                    overall_wordcloud(selected_mentions_wordcloud_data['tweets_no_stopwords'])
            with m_ex_col2:
                m_overall_hashtag_plot(m_hashtagg_category_data)
            m_overall_mentions_plot(m_mensions_category_data)        


        m_posword_col,m_negword_col,m_neuword_col = st.columns((1,1,1))
        with m_posword_col:
            m_positive_wordcloud_expander = st.expander(label='Positive WordCloud')
            with m_positive_wordcloud_expander:
                if len(selected_mentions_positive_wordcloud_data['tweets_no_stopwords']) > 0:
                    positive_wordcloud(selected_mentions_positive_wordcloud_data['tweets_no_stopwords'])
            
        with m_negword_col:
            m_negative_wordcloud_expander = st.expander(label='Negative WordCloud')
            with m_negative_wordcloud_expander:
                if len(selected_mentions_negative_wordcloud_data['tweets_no_stopwords']) > 0:
                    negative_wordcloud(selected_mentions_negative_wordcloud_data['tweets_no_stopwords'])
                
        with m_neuword_col:
            m_neutral_wordcloud_expander = st.expander(label='Neutral WordCloud')
            with m_neutral_wordcloud_expander:
                if len(selected_mentions_neutral_wordcloud_data['tweets_no_stopwords']) > 0:
                    neutral_wordcloud(selected_mentions_neutral_wordcloud_data['tweets_no_stopwords'])
                






        m_hashtag_analysis_expander = st.expander(label='Hashtag Analysis')
        with m_hashtag_analysis_expander:
            m_hashtag_col1,m_hashtag_col2 = st.columns(2)
            with m_hashtag_col1:
                m_uni_hashtag_plot(m_hashtagg_category_data)
            with m_hashtag_col2:
                m_bi_hashtag_plot(m_hashtagg_category_data)
            

            m_hashtag_col3,m_hashtag_col4 = st.columns(2)
            with m_hashtag_col3:
                m_tri_hashtag_plot(m_hashtagg_category_data)        
            with m_hashtag_col4:
                m_multi_hashtag_plot(m_hashtagg_category_data)






        m_mentions_analysis_expander = st.expander(label='Mentions Analysis')
        with m_mentions_analysis_expander:
            m_mentions_col1,m_mentions_col2 = st.columns(2)
            with m_mentions_col1:
                m_uni_mentions_plot(m_mensions_category_data)
            with m_mentions_col2:
                m_bi_mentions_plot(m_mensions_category_data)
            m_tri_mentions_plot(m_mensions_category_data)        

            m_multi_mentions_plot(m_mensions_category_data)


        gb = GridOptionsBuilder.from_dataframe(mentions_overall_data)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            mentions_overall_data,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='blue', #Add theme color to the table
            enable_enterprise_modules=True,
            height=350, 
            width='100%',
            reload_data=True
        )











