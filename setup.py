import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WallStreetSocial",
    version="0.0.0.4",
    author=["Joshua David Golafshan", "John Hutton"],
    description="""Is an open source piece of software that is designed to allow anyone to quickly get
                familiar with the basics of textual analysis. It features a preconfigured database schema, 
                preconfigured pipelines to fill the database with reddit comments, and a pretrained named entity
                recognition model that is used to pull out what stocks are being mentioned in a post.""",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/JGolafshan/WallStreetSocial",
    keywords=["Wall Street Bets"],
    packages=["WallStreetSocial"],
    install_requires=[
        'datetime',
        'pandas',
        'requests',
        'pmaw',
        'vaderSentiment',
    ],
    package_dir=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)


"""
py setup.py sdist
py setup.py bdist_wheel
py -m twine upload --skip-existing dist/*
"""
