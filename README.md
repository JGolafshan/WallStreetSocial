# Wall Street Social
Is an open source piece of software that is designed to allow anyone to quickly get familiar with the basics of textual analysis. It features a preconfigured database schema, preconfigured pipelines to fill the database with reddit comments, and a pretrained named entity recognition model that is used to pull out what stocks are being mentioned in a post.

* [Requirements ](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#requirements)
* [Features and Updates](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#features-and-updates)
* [Introduction](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#features-and-updates)
* [Directory Explained](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#directory-explained)
* [Resources and Dataset Descriptions](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#resources-and-dataset-descriptions)
* [About the ML Model](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#about-the-ml-model)
* [Python Code Example](https://github.com/JGolafshan/WallStreetSocial/blob/master/README.md#python-code-example)
## Requirements 
postgreq 
## Features and Updates
## Introduction
## Directory Explained
## Resources and Dataset Descriptions
## About the ML Model
The named entity recognition model in use is a compact spaCy model which has been trained on wallstreetbets specific data. The model has been trained in two parts: first, Gensim was used to create the word vectors. Word vectors are basically multidimensional representations of words in algebraic space that help the model determine things like word similarity. It helps give the model some form of contextual awareness of the words it is encountering. The model is then trained specifically on data from reddit. The data consists of thousands of comments that have labeled stocks and their respective positions in the text. For a visual representation of the word vectors, please see https://www.kaggle.com/johnhutton/visualization-of-wallstreetbets-word-vectors
## Python Code Example
