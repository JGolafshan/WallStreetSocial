import os
import sqlite3
import pandas.core.frame
import pandas as pd
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from WallStreetSocial.models.model_utils.preprocess import preprocess


class DatabasePipe:
    """
    Setups a database connection as well functions to aid the creation, insertion and alteration of tables
    """

    def __init__(self):
        """
        Description:
            Setups up a database connection and cursor
        Returns:
            None
        """
        self.conn = sqlite3.connect(os.path.dirname(os.path.dirname(__file__)) + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()

    # Private Functions
    @staticmethod
    def _convert_iterator(data):
        """
        Description:
            converts an iterative datatype to a pandas dataframe
        Parameters:
            data (iterator): an iterator datatype such as a dataframe, list, dictionary ect.
        Returns:
            Returns a dataframe
        """
        if isinstance(data, pandas.core.frame.DataFrame) is False:
            data = pd.DataFrame(data)

        data = data.applymap(str)  # TODO
        data = data.convert_dtypes()
        data = data.select_dtypes(exclude=['object'])
        return data

    @staticmethod
    def _insert_meta_data(position, name, datatype, primary_key, foreign_key):
        """
        Description:
            dajsahsadhjadshj
        Parameters:
            position (int): the location of the column in regards to the database
            name (str): column name
            datatype (): the datatype of the column
            primary_key (bool): is column a primary key
            foreign_key (bool): is column a foreign key
        Returns:
            Return a list of the parameters
        """
        return list([position, name, datatype, primary_key, foreign_key])

    @staticmethod
    def _find_related_columns(data):
        """
        Description:
            group columns with similar names
        Parameters:
            data (iterator): an iterator datatype such as a dataframe, list, dictionary ect.
        Returns:
            Returns a List of column
        """

        column_names = data.columns.values.tolist()
        related_columns = []
        for i in column_names:
            first_word = str(i).split("_")[0]
            counter = 0
            for j in column_names:
                if first_word == str(j).split("_")[0]:
                    counter += 1
            if counter >= 2 and first_word not in related_columns:
                related_columns.append(first_word)
        return related_columns

    @staticmethod
    def _table_constraints(meta_data):
        """
        Description:
            Converts _meta_data function into useful sql code
        Parameters:
            meta_data (list): should use self._meta_data
        Returns:
            Returns a str with sql data
        """
        table_contents = ""
        for i in range(len(meta_data)):
            if meta_data[i][4] is True:
                pass
            if meta_data[i][3] is True:
                meta_data[i][2] = "INTEGER PRIMARY KEY AUTOINCREMENT"

            table_contents += f"{meta_data[i][1]} {meta_data[i][2]}"
            if i != len(meta_data) - 1:
                table_contents += ", \n "

        return table_contents

    def _primary_key(self, table, meta_data):
        """
        Description:
        Parameters:
        Returns:
        """
        column_name = table + "_id"
        meta_data.append(self._insert_meta_data(0, column_name, "Integer", True, False))
        return meta_data

    def _meta_data(self, data):
        """
        Description:
            Used in the creation of tables, this function groups up columns with similar names into tables.
            and creates them.
        Parameters:
            data (dataframe): an iterator datatype such as a dataframe, list, dictionary ect.
        Returns:
            Returns a List[Tuple()] structure with with values (position, name, type, pk, fk)
        """
        dataframe = self._convert_iterator(data)
        column_names = dataframe.columns.values.tolist()
        meta_data = []
        for column in range(len(column_names)):
            data_type = dataframe[column_names[column]].dtypes.name
            if data_type == 'Int64':
                data_type = 'Integer'
            meta_data.append(
                self._insert_meta_data(column, column_names[column], str(data_type).capitalize(), False, False))
        return meta_data

    def _create_table(self, table, constraints):
        """
        Description:
            Creates a sqlite table using the parameters
        Parameters:
            table (str): name that is defined for the table
            constraints (str): [[column_name][constraints]] constraints can be  a datatype or key
        Returns:
            Returns Nothing
        """
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table} ({constraints});""")
        self.conn.commit()

    def _alter_table(self, table, constraints):
        """
        Description:
            Adds a column to a existing table
        Parameters:
            table (str): name that is defined for the table
            constraints (list): [[column_name][constraints]] constraints can be  a datatype or key
        Returns:
            None
        """
        self.cursor.execute(f"""ALTER TABLE {table}  ADD COLUMN {constraints};""")
        self.conn.commit()

    def _insert_into_row(self, table, data):
        """
        Description:
        Parameters:
        Returns:
        """
        table_info = data.columns.values.tolist()

        values = "? , " * len(table_info)
        columns = ", ".join(table_info)

        data = data.to_records(index=False).tolist()
        self.cursor.executemany(f"""INSERT INTO {table} ({columns}) VALUES({values[:-2]});""", data, )
        self.conn.commit()

    def _update_row(self, table, data):
        """
        Description:
        Parameters:
        Returns:
        """
        table_info = data.columns.values.tolist()

        values = "? , " * len(table_info)
        columns = ", ".join(table_info)

        data = data.to_records(index=False).tolist()
        self.cursor.executemany(f"""INSERT INTO {table} ({columns}) VALUES({values[:-2]});""", data, )
        self.conn.commit()

    # Public Functions
    def describe_table(self, table):
        """
        Description:
            displays information about an sql table
        Parameters:
            table (str): name that is defined for the table
        Returns:
            Returns a List[Tuple()] structure with with values (cid (position in the table where 1 is
                the first column and n is the last column), name, type, dflt_value, pk)
        """
        return self.cursor.execute(f"PRAGMA table_info({table});").fetchall()

    def er_diagram(self, open_diagram):
        """
        Description:
            Creates a diagram if the database, useful for query design.
        Parameters:
            open_diagram(boolean) - if open is true will open a png of the diagram
        Returns:
            Saves a image of the database
        """

    def transform_dataframe(self, table, data):
        """
        Description:
            Transforms the dataframe, creates, inserts and alterates the database
        Parameters:
            table (str): name that is defined for the table
            data (iterator): an iterator datatype such as a dataframe, list, dictionary ect.
        Returns:
            Returns Nothing
        """
        dataframe = self._convert_iterator(data)
        table_info = self._meta_data(dataframe)
        table_info = self._primary_key(table, table_info)
        constraints = self._table_constraints(meta_data=table_info)
        self._create_table(table, constraints)
        self._insert_into_row(table, dataframe)

    def create_view(self, view_name, query):
        pass

    def create_ticker_table(self):
        """
        Description:
            Creates a new table called ticker which is used for to gather symbols/sentiment from comments and posts
        Parameters:
            Returns Nothing
        Returns:
            Returns Nothing
        """
        self._create_table("ticker",
                           """TickerID integer PRIMARY KEY AUTOINCREMENT, CommentID integer,
                              TickerSymbol VARCHAR(5), TickerSentiment float, 
                              FOREIGN KEY (CommentID) REFERENCES Comment (CommentID)""")

    def create_option_table(self):
        """
        Description:
            Creates a new table called option which is used for to gather symbols/sentiment from comments and posts
        Parameters:
            Returns Nothing
        Returns:
            Returns Nothing
        """
        self._create_table("option",
                           """OptionID INTEGER PRIMARY KEY AUTOINCREMENT,
                              TickerID INTEGER, OptionType VARCHAR(4),
                              OptionStrike FLOAT, OptionExpirationDate DATETIME,
                              OptionContracts INTEGER, OptionPremium FLOAT """)

    def insert_into_ticker(self, comment_id, ticker, sentiment):
        """
        Description:
            Inserts tickers into the Ticker table
        Parameters:
            Returns Nothing
        Returns:
            Returns Nothing
        """
        self.cursor.execute(
            f""" INSERT INTO Ticker (CommentID, TickerSymbol, TickerSentiment) VALUES (?, ?, ?)""",
            (comment_id, str(ticker).upper(), sentiment))
        self.conn.commit()

    def ticker_generation(self):
        """
        Description:
            Uses the the sentiment and ticker models to generate tickers and sentiment for each comment
        Parameters:
            Returns Nothing
        Returns:
            Returns Nothing
        """
        loadData = self.cursor.execute("""SELECT c.comment_id, c.body FROM comment c 
                                          WHERE c.comment_id NOT IN (SELECT t.CommentID FROM ticker t)""").fetchall()
        wsb = spacy.load(os.getcwd() + "/WallStreetSocial/models/wsb_ner")
        sia = SentimentIntensityAnalyzer()
        # Add to Ticker DB
        for row in loadData:
            doc = wsb(preprocess(str(row[1])))
            if len(doc.ents) > 0:
                for ticker in doc.ents:
                    self.insert_into_ticker(row[0], ticker, sia.polarity_scores(row[1])['compound'])
            else:
                self.insert_into_ticker(row[0], None, None)

    def option_generation(self):
        """"""
        pass
