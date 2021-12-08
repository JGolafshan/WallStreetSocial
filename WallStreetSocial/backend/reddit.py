import pprint
from WallStreetSocial.backend import database
from pmaw import PushshiftAPI
import datetime as dt
import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50000)


class RedditPipe:
    """
    This class will be used to pull reddit comments from a specific subreddit over a given time period.
    It pulls from pushshift, arranges comments into a dataframe, removes unnecessary columns, saves it down
    to a file in the temp folder, and then loads them into the postgres database,
    which is set up in the database.py file.
    """

    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def convert_date(self, date):
        """converts a date/datetime  to a unix so that Pushshift can understand it"""
        datetime = str(date).split(" ")
        if len(datetime) == 1:
            datetime = datetime[0] + " 00:00:00"
        else:
            datetime = date

        return int(dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S').timestamp())

    def generic_algorithm(self, subreddits, start, end, comment_filter=None, post_filter=None):
        start = self.convert_date(start)
        end = self.convert_date(end)
        api = PushshiftAPI(shards_down_behavior="None")
        db = database.DatabasePipe()

        print("fetching posts in the data range")
        posts = api.search_submissions(subreddit=subreddits, before=end, after=start)
        post_df = pd.DataFrame(posts)
        dbc_post = database.ModifyDatabase(connection=db, table="post", dataframe=post_df)
        dbc_post.main_function()

        comments = api.search_comments(subreddit=subreddits, before=end, after=start)
        comment_df = pd.DataFrame(comments)
        dbc_comment = database.ModifyDatabase(connection=db, table="comment", dataframe=comment_df)
        dbc_comment.main_function()

    # noinspection PyMethodMayBeStatic
    def log_submissions(self, df):
        """
        Converts the dataframe to CSV which is saved for logging/debugging purposes.
        Which can be found in /dependencies/logs
        """
        dir_name = os.path.dirname(os.path.abspath(__file__))
        folder = 'temp'
        file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M")

        path = f"{dir_name}\{folder}\{file_name}.csv"
        df.to_csv(path, encoding='utf-8-sig', index=False)
        return path
