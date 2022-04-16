import streamlit as st
import pandas as pd
import datetime
import os

import plotly.graph_objects as go

from utils import collect_tweets

# Header
st.image('images/banner.png')

# Enter keywords
with st.form('form1'):
    st.markdown('<h3 style="text-align:center;">Search settings</h3>',
                unsafe_allow_html=True)
    keyword = st.text_input('Enter keyword(s), separated by comma or leave blank')
    col1, col2 = st.columns(2)
    begin_date = col1.date_input('From', datetime.date(2021, 5, 2))
    end_date = col2.date_input('Until', datetime.date(2021, 5, 4),
                               # not working
                               # min_value=begin_date + datetime.timedelta(days=1)
                               )

    with st.expander('Other search settings'):
        # st.markdown('<div style="height: 50px; width: 50px; background-color: #555;"></div>',
        #             unsafe_allow_html=True)
        hashtags_checkbox = st.checkbox('Only tweets with hashtags', False)
        col1, col2 = st.columns(2)
        num_tweets_per_day = col1.number_input('Max number of tweets per day', value=100, step=1)
        min_favs = col1.number_input('Min likes per tweet', value=10, step=1)

    search = st.form_submit_button('Submit')


# Collect data
if search:
    if end_date <= begin_date:
        st.error('Date!')
    else:
        keyword_list = keyword.split(',')
        # Split on whitespace and join words to delete space after the words_
        keyword_list = [' '.join(key.split()) for key in keyword_list]

        dfs = collect_tweets(keywords=keyword_list,
                             only_hashtags=hashtags_checkbox,
                             num_tweets_per_day=num_tweets_per_day,
                             min_favs=min_favs,
                             begin_date=begin_date,
                             end_date=end_date)

        if os.listdir('data'):
            for f in os.listdir('data'):
                os.remove(os.path.join('data', f))

        for name, df in dfs.items():
            df.to_csv('data/' + name + '.csv', index=False)


def load_data():
    dfs_dict = {}
    date_options_ = []

    for f in os.listdir('data'):
        path = os.path.join('data', f)
        date = f.split('.')[0]

        dfs_dict[date] = pd.read_csv(path)
        date_options_.append(date)
    return dfs_dict, date_options_


dfs, date_options = load_data()

if date_options:
    day_selected = st.selectbox(label='date', options=date_options)

    if day_selected in dfs:

        df = dfs[day_selected]

        fig = go.Figure(data=[go.Table(
            columnwidth=[200, 1200],
            header=dict(values=list(df.columns),
                        # fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df.date, df.content],
                       # fill_color='lavender',
                       align='left',
                       font_size=14))
        ])
        fig.update_layout(
            width=1400,
            height=500,
            margin=dict(
                l=0,
                r=0,
                t=0
            )
        )

        st.plotly_chart(fig, use_container_width=True)
