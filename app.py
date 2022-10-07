import streamlit as st
import datetime
import os

from utils.get_data import collect_tweets, load_csvs
from utils.charts import show_table
from utils.preprocess import clean_tweets, text_preprocess
from constants import *

TODAY = datetime.date.today()

# Remove previous data files if any
if os.listdir(DATA_PATH):
    for f in os.listdir(DATA_PATH):
        os.remove(os.path.join(DATA_PATH, f))


# Banner
st.image('images/banner.png')

# Form for entering search parameters
with st.form('form1'):
    st.markdown('<h3 style="text-align:center;">Search settings</h3>',
                unsafe_allow_html=True)
    # Keywords
    keyword = st.text_input('Enter keyword(s) separated by comma, or leave blank')

    # Begin, end date
    col1, col2 = st.columns(2)
    begin_date = col1.date_input('From', TODAY-datetime.timedelta(7), max_value=TODAY)
    end_date = col2.date_input('Until', TODAY, max_value=TODAY)

    # Additional search params
    with st.expander('Other search settings'):
        # Hashtags, likes, num tweets
        hashtags_checkbox = st.checkbox('Only tweets with hashtags', False)
        col1, col2 = st.columns(2)
        num_tweets_per_day = col1.number_input('Max number of tweets per day', value=100, step=1)
        min_favs = col1.number_input('Min likes per tweet', value=0, step=1)
        # Location
        location = st.text_input('Location:')
        col1, col2 = st.columns(2)
        coordinates = col1.text_input('Coordinates:')
        radius = col2.text_input('Radius:')

    # Search button
    search = st.form_submit_button('🔍 Search!')


# ---  Collect data  -----------------------------------------------------------
if search:
    if end_date <= begin_date:
        st.error('Incorrect date!')
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

        # Save dataframes as pdf, one per day
        for name, df in dfs.items():
            df.to_csv(DATA_PATH + '/' + name + '.csv', index=False)


# ---  Load Data  --------------------------------------------------------------
# If data repository is not empty
if any(os.scandir(DATA_PATH)):
    # Load csv files
    # Dict in format {'name': pd.DataFrame}, list of names of the files
    dfs, date_options = load_csvs(DATA_PATH)

    # Show records for a particular day
    if date_options:
        day_selected = st.selectbox(label='date', options=date_options)

        if day_selected in dfs:
            df = dfs[day_selected]
            # Show table
            fig = show_table(df)
            st.plotly_chart(fig, use_container_width=True)

    # Clean tweets: remove hashtags, mentions and other symbols
    dfs_cleaned = {}
    for day in date_options:
        dfs_cleaned[day] = clean_tweets(dfs[day])

    # if date_options:
    #     day_selected = st.selectbox(label='date', options=date_options, key=2)
    #
    #     if day_selected in dfs:
    #         df = dfs_cleaned[day_selected]
    #         fig = show_table(df)
    #         st.plotly_chart(fig, use_container_width=True)

    # Preprocess: tokenize, remove stop-words, lemmatize, apply stemming
    for day in date_options:
        df = dfs_cleaned[day]
        df['content_preprocessed'] = [text_preprocess(t, stop_words=True, lemmatize=True) for t in df['content_cleaned']]
        df['content_preprocessed_with_stopwords'] = [text_preprocess(t) for t in df['content_cleaned']]

    # if date_options:
    #     day_selected = st.selectbox(label='date', options=date_options, key=3)
    #
    #     if day_selected in dfs:
    #         df = dfs_cleaned[day_selected]
    #         fig = show_table(df)
    #         st.plotly_chart(fig, use_container_width=True)



