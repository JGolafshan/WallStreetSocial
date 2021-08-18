import datetime as dt
import pandas as pd
from pmaw import PushshiftAPI
import re
from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
import os
from pprint import pprint

# input true for sandbox
def sandbox(change):
    if change:
        # Set IEX Finance API Token for Sandbox test mode
        os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
        os.environ['IEX_TOKEN'] = 'Tsk_4060833567884b49870980c4a917aa92'
    else:
        # Real
        os.environ['IEX_API_VERSION'] = 'stable'
        os.environ['IEX_TOKEN'] = ''


sandbox(True)

before = int(dt.datetime(2014, 1, 2, 0, 0).timestamp())
after = int(dt.datetime(2014, 1, 1, 0, 0).timestamp())


def get_reddit_comments(subreddit, before, after):
    """Returns a dataframe containing comments from a particular subreddit between
       given date frame defined by before and after.
       Before and after variables must be converted to epoch time before calling them as arguments.
    """
    api = PushshiftAPI()
    comments = api.search_comments(subreddit=subreddit, before=before, after=after)
    comments_df = pd.DataFrame(comments)
    comments_df = clean_comments_dataframe(comments_df)
    return comments_df


def clean_comments_dataframe(comments_df):
    try:
        comments_df = comments_df.drop(
            ['all_awardings', 'associated_award', 'author_flair_background_color', 'author_flair_css_class',
             'author_flair_richtext',
             'author_flair_template_id', 'author_flair_text', 'author_flair_text_color', 'author_flair_type',
             'author_fullname', 'author_patreon_flair', 'author_premium', 'awarders', 'collapsed_because_crowd_control',
             'comment_type', 'gildings', 'is_submitter', 'locked', 'no_follow', 'send_replies', 'top_awarded_type',
             'treatment_tags', 'author_cakeday', 'distinguished'], axis=1)
    except KeyError:
        return comments_df
    return comments_df


def comments_to_csv(comments_df):
    """
    Saves down comments_df to a csv for loading into a data table
    """
    file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M") + '.csv'
    comments_df.to_csv(file_name, encoding='utf-8-sig', index=False)
    return file_name


def find_tickers(comment):
    """
    Creates an initial list of "tickers" in the form $XYZ to be verified by sending the string to IEX. If we get a price
    back,we will add the ticker it into a table in our database, "MENTIONED_STOCKS" if it is not already in it.
    This function willrun through all comments in a batch, and then the verified MENTIONED_STOCKS will be used to look
    through each comment again to find tickers that aren't marked with $. This function acts on a single comment.
    """
    tickers = re.findall(r'\$[a-zA-Z]+\b', str(comment))
    return tickers


def verify_tickers(tickers):
    """
    Verifies if a ticker is real by sending it to the IEX. If the API call doesn't error out, we assume it to be a real
    ticker and append it to a list of mentioned tickers. This function acts on a single comment.
    """
    mentioned_tickers = []
    for ticker in tickers:
        try:
            price = Stock(ticker[1:]).get_company()
            mentioned_tickers.append(ticker[1:])
        except Exception as e:
            pass

    return mentioned_tickers


def create_master_ticker_list(comments):
    """
    Takes in a list of comments and searches through them to create a master list of mentioned comments per batch
    Returns a dataframe list of stocks to be loaded into the MENTIONED_STOCKS table.
    """
    verified_tickers = []
    for comment in comments:
        tickers = find_tickers(comment)  # get list of tickers in a comment
        mentioned_tickers = verify_tickers(tickers)  # verify if they're real
        for ticker in mentioned_tickers:
            verified_tickers.append(ticker)
    return verified_tickers


x = get_reddit_comments("wallstreetbets", before=before, after=after)

pprint(x)
