import datetime
import itertools
import pandas as pd
import re
import snscrape.modules.twitter as sntwitter
import streamlit as st

import time


# --- Collect data -------------------------------------------------------------
def collect_tweets(begin_date=datetime.date(2021, 5, 1),
                   end_date=datetime.date(2021, 5, 3),
                   keywords=False,
                   min_favs=10,
                   only_hashtags=False,
                   city=False,
                   radius=False,
                   geocode=False,
                   num_tweets_per_day=10
                   ):
    """
    Collects posts from Twitter by given params

    Accepts:
    --> begin_date - datetime.date object
    --> end_date - datetime.date object, NOT INCLUDED
    --> keywords - list of strings
    --> min_faves - int, minimum likes for tweet
    --> only_hashtags - bool, if True - collect only tweets with hashtags
    --> city - string (e.g. san-francisco)
    --> radius - string (e.g. 10km), works only with city
    --> geocode - coordinates (lat,long,radius; e.g. 37.7764685,-122.4172004,10km)
    --> num_tweets_per_day --> int, there may be less tweets if enough haven't been found

    Returns a dictionary, where:
    --> key - string date in format Y-m-d
    --> value - DataFrame with columns 'date' and 'content',
        which contains collected tweets on a certain day

    """

    # initialize query
    # add keywords to query if given
    if keywords:
        keywords = ' OR '.join(keywords)
        print('\n\n', keywords, '\n\n')
        search = keywords
        search = search + ' lang:en' + ' min_faves:{}'.format(min_favs)
    else:
        search = 'lang:en' + ' min_faves:{}'.format(min_favs)

    if only_hashtags:
        search = search + ' filter:hashtags'

    if city:
        search = search + ' near:{}'.format(city)

    if city and radius:
        search = search + ' near:{}'.format(city) + ' within:{}'.format(radius)

    if geocode:
        search = search + ' geocode:{}'.format(geocode)

    # get date interval
    days = end_date - begin_date

    dataframes = {}

    # Percentage increment, add placeholder for request, progress bar
    percent_increment = 1. / days.days
    percent_current = 0
    placeholder = st.empty()
    my_bar = st.progress(percent_current)

    for day in range(1, days.days + 1):
        today = begin_date
        tomorrow = today + datetime.timedelta(days=1)

        # dates to string
        today_str = today.strftime('%Y-%m-%d')
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')

        # progress bar
        my_bar.progress(percent_current)
        # placeholder.markdown(f'Searching for tweets on day <b>{today_str}</b>',
        #                      unsafe_allow_html=True)

        # search tweets by query
        search_new = search + ' since:{}'.format(today_str) + ' until:{}'.format(tomorrow_str)
        placeholder.write(f'Request: {search_new}')
        scraped_tweets = sntwitter.TwitterSearchScraper(search_new).get_items()

        # get necessary number of tweets
        sliced_scraped_tweets = itertools.islice(scraped_tweets, num_tweets_per_day)

        # turn collected tweets into dataframe
        df = pd.DataFrame(sliced_scraped_tweets)

        if len(df) > 0:
            df = df[['date', 'content']]
        else:
            df = pd.DataFrame(columns=['date', 'content'])

        # add dataframe to dictionary
        dataframes[today_str] = df

        # move to next day
        begin_date += datetime.timedelta(days=1)

        # increase progress
        percent_current += percent_increment

    # Empty progress bar and labels
    my_bar.empty()
    placeholder.empty()
    placeholder.success('All data collected!')
    time.sleep(1.5)
    placeholder.empty()

    return dataframes


# --- Clean data ---------------------------------------------------------------

def clean_tweets(df, keywords=False):
    """
    Accepts dataframe with 'content' column and list of keywords
    Adds columns 'content_cleaned', 'hashtags'
    Returns old dataset with new columns

    """
    df = df.copy()
    cleaned = []
    hashtags = []

    for tweet in df['content']:
    #     # replace emojis with words (meanings)
    #     tweet = emoji.demojize(tweet)

        if keywords:
            # delete keywords if given
            for keyword in keywords:
                tweet = re.sub(keyword.lower(), '', tweet)
                tweet = re.sub(keyword.upper(), '', tweet)
                tweet = re.sub(keyword.title(), '', tweet)

        # find all hashtags
        hashtag = re.findall(r'#(\w+)', tweet)

        tweet = re.sub('n[\'’]t', ' not', tweet)

        # remove urls
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        tweet = url_pattern.sub(r'', tweet)

        # remove mentions
        tweet = re.sub('\S*@\S*\s?', '', tweet)

        # remove non-english symbols
        tweet = re.sub('[^\x00-\x7f]', '', tweet)

        # remove new line characters
        tweet = re.sub('\s+', ' ', tweet)

        tweet = re.sub('_', ' ', tweet)

        # remove other symbols
        tweet = re.sub(r'[^\w\s]', ' ', tweet)

        # remove numbers
        tweet = re.sub('\d+', ' ', tweet)

        tweet = re.sub('amp', '', tweet)

        # remove redundant whitespaces
        tweet = tweet.strip()

        cleaned.append(tweet)
        hashtags.append(hashtag)

    df['content_cleaned'] = cleaned
    df['hashtags'] = hashtags

    return df
