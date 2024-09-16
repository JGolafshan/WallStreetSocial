# Wall Street Social
Is an open source piece of software that is 
designed to allow anyone to quickly get familiar with the basics of textual analysis. It features a preconfigured database schema, preconfigured pipelines to fill the database with reddit comments, and a pretrained named entity recognition model that is used to pull out what stocks are being mentioned in a post.

## Getting Starting
This project model doesn't fit the pypi size specifications, to get this project working you will need the these steps.

```
pypi WallStreetBets
```

Download Model [here](https://github.com/JGolafshan/WallStreetSocial/blob/master/wsb_ner.zip)

unzip anywhere

```
from WallStreetSocial import helpers

# Uses model to find ticks in the data comment table
helpers.validate_model('C:Projects\\WallStreetSocial\\wsb_ner')

# Fetches Comments and Posts from a subreddit between two dates
helpers.run("WallStreetBets", start="2019-01-03", end="2019-02-04")


symbol = helpers.SummariseBase(symbol="AAPL")
symbol.display_stats()

```

## About the ML Model
The named entity recognition model in use is a compact spaCy model which has been trained on wallstreetbets specific data. The model has been trained in two parts: first, Gensim was used to create the word vectors. Word vectors are basically multidimensional representations of words in algebraic space that help the model determine things like word similarity. It helps give the model some form of contextual awareness of the words it is encountering. The model is then trained specifically on data from reddit. The data consists of thousands of comments that have labeled stocks and their respective positions in the text. For a visual representation of the word vectors, please see https://www.kaggle.com/johnhutton/visualization-of-wallstreetbets-word-vectors


## TODO
create a simple html interface for a symbol
speed up ticker generation
fix path locations
