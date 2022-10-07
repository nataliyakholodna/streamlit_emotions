import emoji
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter

nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

from nltk.corpus import wordnet

STOPWORDS = set(stopwords.words('english'))

def clean_tweets(df, keywords=None):
    """
    Accepts dataframe with 'content' column and list of keywords
    Adds columns 'content_cleaned', 'hashtags'
    Returns old dataset with new columns

    """
    df = df.copy()
    cleaned = []
    hashtags = []

    for tweet in df['content']:
        # replace emojis with words (meanings)
        tweet = emoji.demojize(tweet)

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


def get_part_of_speech(word):
    '''
    Accepts word
    Returns part of speech tag ('n' - noun, 'v' - verb, 'a' - adjective, 'r' - adverb)

    POS-tag is used as a second argument for better results in lemmatization

    '''
    # get a set of synonyms for the word
    probable_part_of_speech = wordnet.synsets(word)

    pos_counts = Counter()

    # set each value to the number of synonyms that fall into each part of speech
    pos_counts["n"] = len([item for item in probable_part_of_speech if item.pos()=="n"])
    pos_counts["v"] = len([item for item in probable_part_of_speech if item.pos()=="v"])
    pos_counts["a"] = len([item for item in probable_part_of_speech if item.pos()=="a"])
    pos_counts["r"] = len([item for item in probable_part_of_speech if item.pos()=="r"])

    # return the most common part of speech
    most_likely_part_of_speech = pos_counts.most_common(1)[0][0]

    return most_likely_part_of_speech


def text_preprocess(text,
                    stop_words=False, stem=False, lemmatize=False, keywords=False):
    '''
    Accepts text (a single string), parameters of preprocessing (bool) and
    a list of keywords (strings) to delete
    Returns preprocessed text

    '''
    # clean text from non-words
    text = text.lower()

    # tokenize the text
    tokens = word_tokenize(text)

    if keywords:
        # delete keywords
        tokens = [token for token in tokens if token.lower() not in keywords]
        tokens = [token for token in tokens if token.upper() not in keywords]
        tokens = [token for token in tokens if token.title() not in keywords]

    if stop_words:
        # delete stop_words
        tokens = [token for token in tokens if token not in STOPWORDS]

    if stem:
        # apply stemming
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]

    if lemmatize:
        # lemmatize tokens
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token, get_part_of_speech(token)) for token in tokens]

    return tokens
