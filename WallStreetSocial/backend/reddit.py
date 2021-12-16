from WallStreetSocial.backend import database
from pmaw import PushshiftAPI
import datetime as dt
import os


class RedditPipe:
    """
    This class will be used to pull reddit comments from a specific subreddit over a given time period.
    It pulls from pushshift, arranges comments into a dataframe, removes unnecessary columns, saves it down
    to a file in the temp folder, and then loads them into the sqlite database, this process is automated it
    """

    def __init__(self):
        pass

    @staticmethod
    def convert_date(date):
        """
        Description:
            converts a date/datetime to a unix timestamp so that Pushshift can understand it
        Parameters:
            date (str): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
        Returns:
            Returns a unix timestamp
        """

        datetime = str(date).split(" ")
        if len(datetime) == 1:
            datetime = datetime[0] + " 00:00:00"
        else:
            datetime = date

        return int(dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S').timestamp())

    @staticmethod
    def log_submissions(df):
        """
        Description:
            Converts a dataframe to CSV which is saved for logging/debugging purposes.
                Which can be found in /dependencies/logs
        Parameters:
            df (dataframe): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
        Returns:
            Returns a unix timestamp
        """
        dir_name = os.path.dirname(os.path.dirname(__file__))
        folder = 'temp'
        file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M")
        path = f"{dir_name}\{folder}\{file_name}.csv"
        df.to_csv(path, encoding='utf-8-sig', index=False)
        return path

    def generic_algorithm(self, subreddits, start, end):

        start = self.convert_date(start)
        end = self.convert_date(end)
        api = PushshiftAPI(shards_down_behavior="None")
        db = database.DatabasePipe()

        print("fetching posts in the data range")
        posts = api.search_submissions(subreddit=subreddits, before=end, after=start)
        db.transform_dataframe("post", posts)

        print("fetching comments in the data range")
        comments = api.search_comments(subreddit=subreddits, before=end, after=start)
        db.transform_dataframe("comment", comments)

        db.create_ticker_table()
        db.ticker_generation()
        db.create_option_table()
        db.option_generation()
