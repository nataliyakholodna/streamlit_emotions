import os
import pandas as pd


def del_folder_content(path):
    if os.listdir(path):
        for f in os.listdir(path):
            os.remove(os.path.join(path, f))


def most_popular_to_days(dfs, days,  words_or_hashtags='h', min_occur=2, num_words=20):
    '''
    Counts most popular words or hashtags in dataframe
    Accepts:
    --> dfs - a dictionary where key is a str date, value - dataframe
        with 'hashtags', 'content_preprocessed' columns
    --> words_or_hashtags - 'h' or 'w' - what to count
    --> min_occur - int, minimum of how many times word or hashtag appeared
    --> num_words - int, how many most popular words to return

    Returns a dictionary, where:
    --> key - string date in format Y-m-d
    --> value - DataFrame with columns 'word' and 'num',

    '''
    words_counts_arr = []

    if words_or_hashtags=='h':
        column = 'hashtags'
    else:
        column = 'content_preprocessed'

    for day in days:
        # create an array of dictionaries
        # with words and their counts for each day
        words_counts = {}
        for string in dfs[day][column]:
            for word in string:
                if word not in words_counts:
                    words_counts[word] = 1
                else:
                    words_counts[word] += 1
        words_counts_arr.append(words_counts)

    words_to_days = {}
    # create a dictionary with dates and dataframes
    for i, day in enumerate(days):
        df_popular = pd.DataFrame({'word': words_counts_arr[i].keys(),
                                   'num': words_counts_arr[i].values()})
        # select most popular
        df_popular = df_popular.sort_values(by=['num'], ascending=False)
        df_slice = df_popular[df_popular.num >= min_occur]
        df_slice = df_slice[:num_words]

        words_to_days[day] = df_slice

    return words_to_days
