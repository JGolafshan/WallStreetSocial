from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="WallStreetSocial",
    version="1.0.0.3",
    author=["Joshua David Golafshan", "John Hutton"],
    description="""Is an open source piece of software that is designed to allow anyone to quickly get
                    familiar with the basics of textual analysis.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JGolafshan/WallStreetSocial",
    keywords=["Database", "WallStreetBets", "Reddit"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['setuptools',
                      'yfinance',
                      'matplotlib',
                      'pandas',
                      'plotly',
                      'gensim',
                      'datetime',
                      'pmaw',
                      'spacy',
                      'vaderSentiment',
                      'numpy',
                      'nltk',
                      'requests',
                      ],
    classifiers=["Programming Language :: Python :: 3",
                 "Operating System :: OS Independent",
                 ]
)

"""
py setup.py sdist
py setup.py bdist_wheel
py -m twine upload --skip-existing dist/*
"""
