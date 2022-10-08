import streamlit as st
import pandas as pd
import datetime
import os

from tensorflow import keras
import pickle

from utils.get_data import collect_tweets, load_csvs
from utils.charts import show_table, show_bar
from utils.preprocess import clean_tweets, text_preprocess
from utils.predict import predict
from utils.utils import del_folder_content, most_popular_to_days
from constants import *

import plotly.graph_objects as go

TODAY = datetime.date.today()

# Banner
st.image('images/banner.png')

# ---  Form for entering search parameters  ------------------------------------
with st.form('form1'):
    st.markdown('<h3 style="text-align:center;">Search settings</h3>',
                unsafe_allow_html=True)
    # Keywords
    keyword = st.text_input('Enter keyword(s) separated by comma, or leave blank')

    # Begin, end date
    col1, col2 = st.columns(2)
    begin_date = col1.date_input('From', TODAY - datetime.timedelta(7), max_value=TODAY)
    end_date = col2.date_input('Until', TODAY, max_value=TODAY)

    # Additional search params
    with st.expander('Other search settings'):
        # Hashtags, min likes, max num of tweets
        hashtags_checkbox = st.checkbox('Only tweets with hashtags', False)
        col1, col2 = st.columns(2)
        num_tweets_per_day = int(col1.number_input('Max number of tweets per day',
                                                   value=10, step=1,
                                                   min_value=1))
        min_favs = int(col1.number_input('Min likes per tweet',
                                         value=0, step=1,
                                         min_value=0))
        # Location by name or coordinates
        location = st.text_input('Location:')
        col1, col2 = st.columns(2)
        coordinates = col1.text_input('Coordinates:')
        radius = col2.text_input('Radius:')

    # Search button
    search_btn = st.form_submit_button('🔍 Search!')


# ---  Collect data  -----------------------------------------------------------
if search_btn:
    # Start date can not be later that end date
    if end_date <= begin_date:
        st.error('Incorrect date!')
    else:
        # Split keywords into a list
        keyword_list = keyword.split(',')
        # Remove extra whitespaces for each keyword
        keyword_list = [k.strip() for k in keyword_list]

        # Collect tweets and save them to dict in the following format:
        # {'YYYY-MM-DD': pd.Dataframe(columns=['date', 'content'])}
        dfs = collect_tweets(keywords=keyword_list,
                             only_hashtags=hashtags_checkbox,
                             num_tweets_per_day=num_tweets_per_day,
                             min_favs=min_favs,
                             begin_date=begin_date,
                             end_date=end_date)

        # Remove previous results (files) af any
        del_folder_content(DATA_PATH)
        del_folder_content(PREPROCESSED_DATA_PATH)
        del_folder_content(EMOTION_COUNTS_PATH)

        # Save collected raw data, named in format 'YYYY-MM-DD.csv'
        for name, df in dfs.items():
            df.to_csv(DATA_PATH + '/' + name + '.csv', index=False)


# ---  Load RAW Data  ----------------------------------------------------------
if any(os.scandir(DATA_PATH)):
    # 1: Dict in format {'YYYY-MM-DD': pd.Dataframe(columns=['date', 'content'])}
    # 2: List of the file names (['YYYY-MM-DD', ...])
    dfs, date_options = load_csvs(DATA_PATH)

    # Count number of tweets collected every day
    count_tweets = {k: len(df) for k, df in dfs.items()}
    st.markdown('##')  # Space before element
    st.write('\nThe following number of tweets was found:')
    col1, col2 = st.columns([2, 1])
    # Show number of collected tweets per day via bar chart
    fig = show_bar(count_tweets.keys(), count_tweets.values())
    col1.plotly_chart(fig, use_container_width=True)
    # Convert counts to dataframe and display to the right side to bar chart
    col2.dataframe(pd.DataFrame.from_dict(count_tweets, orient='index'), height=180)

    # Show records for a particular day
    if date_options:
        st.markdown('##')
        day_selected = st.selectbox(label='View by date:', options=date_options)
        if day_selected in dfs:
            # Select the corresponding dataframe
            df = dfs[day_selected]
            # Show table
            fig = show_table(df)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('##')
    if st.button('📈 Analyze!'):

        # ---  Preprocess  -----------------------------------------------------
        # Clean tweets: remove hashtags, mentions and other symbols
        dfs_cleaned = {}
        for day in date_options:
            dfs_cleaned[day] = clean_tweets(dfs[day])

        # Preprocess: tokenize, remove stop-words, lemmatize, apply stemming
        for day in date_options:
            df = dfs_cleaned[day]
            df['content_preprocessed'] = [text_preprocess(t, stop_words=True, lemmatize=True) for t in
                                          df['content_cleaned']]
            df['content_preprocessed_with_stopwords'] = [text_preprocess(t) for t in df['content_cleaned']]

        # ---  Obtain Predictions  -----------------------------------------------------
        with st.spinner('Predicting...'):
            # Load pretrained model
            model = keras.models.load_model('models/lstm/content/lstm_model')
            # Load pretrained tokenizer
            with open('tokenizers/lstm/tokenizer.pickle', 'rb') as t:
                tokenizer = pickle.load(t)

            no_emotion, anger, fear, happiness, sadness, surprise = [], [], [], [], [], []
            hashtags = []

            for i, day in enumerate(date_options):
                # Predict labels for each record in the dataframe
                emotions = predict(dfs_cleaned[day]['content_preprocessed_with_stopwords'], model, tokenizer)
                # Add decoded predicted labels to the original dataframe
                dfs[day]['predicted_labels'] = [LABELS_TO_EMOTIONS[i] for i in emotions]

                # Count number of each emotion type for the current date
                no_emotion.append(emotions.count(0))
                anger.append(emotions.count(1))
                fear.append(emotions.count(3))
                happiness.append(emotions.count(4))
                sadness.append(emotions.count(5))
                surprise.append(emotions.count(6))

                # Calculate most popular words or hashtags for the current day
                words_to_days = most_popular_to_days(dfs_cleaned,
                                                     date_options,
                                                     'words',
                                                     num_words=10,
                                                     min_occur=1)
                # st.write(words_to_days)

                #
                hash_today = words_to_days[day]['word'].values
                hashtags.append(', '.join(hash_today))

            # Create a dataframe with emotion counts
            emotion_counts = pd.DataFrame({
                'Date': date_options,
                'no emotion': no_emotion,
                'anger': anger,
                'fear': fear,
                'happiness': happiness,
                'sadness': sadness,
                'surprise': surprise,
                'hashtags': hashtags
            })

        # Remove previous data files if any
        del_folder_content(PREPROCESSED_DATA_PATH)
        del_folder_content(EMOTION_COUNTS_PATH)

        # Replace original datafiles by datafiles with predictions
        for name, df in dfs.items():
            df.to_csv(DATA_PATH + '/' + name + '.csv', index=False)

        # Save preprocessed data
        for name, df in dfs_cleaned.items():
            df.to_csv(PREPROCESSED_DATA_PATH + '/' + name + '.csv', index=False)

        # Save counts ('Date', '# no_emotion', '# happiness', ...)
        emotion_counts.to_csv(EMOTION_COUNTS_PATH + '/emotion_counts.csv', index=False)

if any(os.scandir(EMOTION_COUNTS_PATH)):
    emotion_counts = pd.read_csv(EMOTION_COUNTS_PATH + '/emotion_counts.csv')
    st.dataframe(emotion_counts)

    if emotion_counts.hashtags.isnull().all():
        emotion_counts.hashtags = emotion_counts.hashtags.astype(str)

    ###############
    ###  TO DO  ###
    ###############

    fig = go.Figure()

    # preprocess hashtags for each day
    # for hint on hover

    hvr = []
    for i in range(len(emotion_counts)):
        # split string with hashtags
        txt = emotion_counts['hashtags'].loc[i].split(',')
        # clean whitespaces
        txt = [t.strip() for t in txt]
        # create an array of strings for each day
        txttt = ''
        for j in txt:
            txttt += j + '<br>'
        if txttt == '<br>':
            txttt = 'None'
        hvr.append(txttt)

    hover = 'Date: %{x}' + '<br>Num tweets: %{y}<br>' + '--------------<br>Hashtags:<br>--------------<br><b>%{text}</b>'

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['no emotion'],
                             name='no emotion',
                             line=dict(color='#4895ef'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['anger'],
                             name='anger',
                             line=dict(color='#4361ee'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['fear'],
                             name='fear',
                             line=dict(color='#3f37c9'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['happiness'],
                             name='happiness',
                             line=dict(color='#f72585'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['sadness'],
                             name='sadness',
                             line=dict(color='#7209b7'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.add_trace(go.Scatter(x=emotion_counts['Date'],
                             y=emotion_counts['surprise'],
                             name='surprise',
                             line=dict(color='#b5179e'),
                             hovertemplate=hover,
                             text=hvr, fill='tozeroy'))

    fig.update_layout(hovermode='closest',
                      margin=dict(l=0, r=0),
                      )
    st.plotly_chart(fig, use_container_width=True)
