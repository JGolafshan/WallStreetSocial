import datetime as dt
import os
import ijson
import pandas as pd
from pmaw import PushshiftAPI
from WallStreetSocial import database
from database import Comment


def validate_model(path):
    """
    checks to see if the user has specified a path for the model
    """
    if database.model_loc == '':
        exit("model has no location - please use this link to download the model\n"
             "https://github.com/JGolafshan/WallStreetSocial/blob/master/wsb_ner.zip")
    if os.path.isdir(path) is False:
        exit("could not find path")
    else:
        database.model_loc = path
        print("Model Found!")
        return database.model_loc


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
    dir_name = os.path.dirname(os.getcwd())
    folder = 'temp'
    file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M")
    path = f"{dir_name}\{folder}\{file_name}.csv"
    df.to_csv(path, encoding='utf-8-sig', index=False)
    return path


def preprocess_json_file(input_path, output_path):
    """
    Preprocesses a JSON file with multiple concatenated objects to create a valid JSON array.

    :param input_path: Path to the input JSON file with concatenated objects.
    :param output_path: Path to the output file with a valid JSON array.
    """
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write('[')
        first = True
        for line in infile:
            if not first:
                outfile.write(',')
            first = False
            outfile.write(line.strip())
        outfile.write(']')


def process_json_file(file_path):
    db = database.DatabasePipe()
    with open(file_path, 'r', encoding='utf-8') as file:
        objects = ijson.items(file, 'item')
        db.insert_into_row(Comment, objects)
        db.ticker_generation()


def run(subreddits, start, end):
    """
    Fetches comments and posts from a subreddit between a date range
    adds it to the database,
    then it create tick entries inside the ticker table
    """

    start = convert_date(start)
    end = convert_date(end)
    api = PushshiftAPI(shards_down_behavior="None")
    db = database.DatabasePipe()

    print("fetching posts in the data range")
    posts = api.search_submissions(subreddit=subreddits, before=end, after=start)
    posts_df = pd.DataFrame(posts.responses)
    posts_df = posts_df.filter(["author", "subreddit", "url", "title", "created_utc", "score"])
    db.insert_into_row("post", posts_df)

    print("fetching comments in the data range")
    comments = api.search_comments(subreddit=subreddits, before=end, after=start)
    comment_df = pd.DataFrame(comments.responses)
    comment_df = comment_df.filter(["permalink", "subreddit", "author", "body", "score", "created_utc"])
    db.insert_into_row("comment", comment_df)

    db.ticker_generation()
