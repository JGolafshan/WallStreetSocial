import sys
import os

# Add the virtual environment's site-packages to the path
venv_site_packages = os.path.join(os.getcwd(), 'venv', 'Lib', 'site-packages')
sys.path.append(venv_site_packages)
from WallStreetSocial import helpers
import database

# Uses model to find ticks in the data comment table
# helpers.validate_model('C:\\Users\\JGola\\Documents\\GitHub\\WallStreetSocial\\wsb_ner\\wsb_ner')

# Fetches Comments and Posts from a subreddit between two dates
# helpers.run("wallstreetbets", start="2019-01-03", end="2024-02-04")


# Using a existing dataset to
input_path = 'dataset/wsbData_unzipped.json'
output_path = 'dataset/wsbData_processed.json'
# helpers.preprocess_json_file(input_path, output_path)
json_data = helpers.process_json_file(output_path)

x = database.DatabasePipe()
x.unique_symbols()

# x = helpers.SummariseBase("TSLA", "wallstreetbets")
# print(x.display_stats())
