import datetime as dt
import pandas as pd
from pmaw import PushshiftAPI
import os

from database import Database



before = int(dt.datetime(2021, 1, 2, 11, 59).timestamp())
after = int(dt.datetime(2021, 1, 2, 11, 58).timestamp())


class RedditPull:
    """
    This class will be used to pull reddit comments from a specific subreddit over a given time period.
    It pulls from pushshift, arranges comments into a dataframe, removes unnecessary columns, saves it down
    to a file in the temp folder, and then loads them into the postgres database,
    which is set up in the database.py file.
    """

    def __init__(self, subreddit, before, after):
        self.dir_name = os.path.dirname(os.path.abspath(__file__))
        self.before = before
        self.after = after
        self.subreddit = subreddit
        self.comments_df = self.GetRedditComments()
        self.final_df = self.CreateFinalDataframe(self.comments_df)
        self.path = self.CommentsToCsv(self.final_df)
        self.db = Database()
        self.execute = self.db.redditDump(self.db.conn, self.db.cursor, self.path)




    def GetRedditComments(self):
        """Returns a dataframe containing comments from a particular subreddit between
              given date frame defined by before and after.

              Before and after variables must be converted to epoch time before calling them as arguments.
           """
        api = PushshiftAPI()
        comments = api.search_comments(subreddit=self.subreddit, before=self.before, after=self.after)
        comments_df = pd.DataFrame(comments)
        return comments_df

    def CreateFinalDataframe(self, df):
        clean_df = df[['id','created_utc','body']]
        clean_df['created_utc'] = pd.to_datetime(clean_df['created_utc'], unit='s')
        clean_df = clean_df.replace(',','',regex=True)
        clean_df = clean_df.replace('\n','',regex = True)
        return clean_df

    def CommentsToCsv(self, df):
        file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M") + '.csv'
        folder = 'temp'
        path = f"{self.dir_name}\{folder}\{file_name}"
        df.to_csv(path, encoding='utf-8-sig', index=True)
        return path









wsb = RedditPull('wallstreetbets',before, after)

