from WallStreetSocial.backend import reddit
from WallStreetSocial.backend import database

reddit = reddit.RedditPipe()
createDB = database.DatabasePipe()
# comment_filter=["id", "body", "created_utc"], post_filter=["id", "selftext", "title", "created_utc"]

reddit.generic_algorithm("WallStreetBets", start="2020-08-05 00:00:00", end="2020-08-05 00:02:40")

