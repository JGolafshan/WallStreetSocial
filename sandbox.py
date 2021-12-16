from WallStreetSocial.backend import reddit


reddit = reddit.RedditPipe()
reddit.run("WallStreetBets", start="2020-08-03 00:00:00", end="2020-08-03 03:01:40")
