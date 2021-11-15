from pmaw import PushshiftAPI
import datetime as dt
import pandas as pd
import os


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
        """converts a date/datetime to a format that Pushshift can read"""
        datetime = str(date).split(" ")
        if len(datetime) == 1:
            datetime = datetime[0] + " 00:00:00"
        else:
            datetime = datetime[0] + " " + datetime[1]

        return int(dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S').timestamp())

    def retrieve_submissions(self, subreddit, start, end):
        """
        Returns a dataframe containing comments from a particular subreddit between
        given date frame defined by before and after.
        Before and after variables must be converted to epoch time before calling them as arguments.
        """
        end = self.convert_date(end)
        start = self.convert_date(start)

        api = PushshiftAPI()
        comments = api.search_comments(subreddit=subreddit, before=end, after=start)
        comments_df = pd.DataFrame(comments)
        return comments_df

    # noinspection PyMethodMayBeStatic
    def clean_submissions(self, df):
        """Cleans data, removes unwanted fields"""
        clean_df = df.loc[:, ['id', 'created_utc', 'body']]
        clean_df['created_utc'] = pd.to_datetime(df["created_utc"],  unit='s', errors='ignore')
        clean_df = clean_df.replace({"body": {',': '', '\n': '', "'": '', '"': '', r'http\S+': ''}}, regex=True)
        return clean_df

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