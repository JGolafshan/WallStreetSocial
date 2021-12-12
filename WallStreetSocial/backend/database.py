import os
import sqlite3


class DatabasePipe:
    """This class is used for the creation of an sqlite database"""

    def __init__(self, table, dataframe):
        """"""
        self.table = table
        self.dataframe = dataframe
        self.conn = sqlite3.connect(os.path.dirname(os.path.dirname(__file__)) + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()

    def run(self):
        """"""
        self.create_dependency_tables()
        self.create_table()
        self.insert_rows()

    def create_meta_data(self):
        """Returns a 2D list that contains the"""
        self.dataframe = self.dataframe.applymap(str)  # remove once dependency tables are made
        self.dataframe = self.dataframe.convert_dtypes()
        column_names = self.dataframe.columns.values.tolist()
        column_constrains = []

        for name in column_names:
            data_type = self.dataframe[name].dtypes.name
            if data_type == 'Int64':
                column_constrains.append('integer'.capitalize())
            else:
                column_constrains.append(str(self.dataframe[name].dtypes.name).capitalize())

        return [list(t) for t in zip(column_names, column_constrains)]

    def create_table(self):
        """"""
        meta_data = self.create_meta_data()
        _meta_data = self.set_primary_key(meta_data=meta_data)
        columns = [' '.join(m) for m in _meta_data]
        columns = ", ".join(columns)
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} ({columns});""")
        self.conn.commit()

    def add_column(self, meta_data):
        """"""
        self.cursor.execute(f"""ALTER TABLE {self.table}  ADD COLUMN {meta_data};""")
        self.conn.commit()

    def set_primary_key(self, meta_data):
        """"""
        for i in range(len(meta_data)):
            if meta_data[i][0] == "id":
                meta_data[i].append("PRIMARY KEY")
                break
        else:
            meta_data.append([f"{self.table}__id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"])

        return meta_data

    def verify_column_persistence(self):
        """"""
        db_columns = self.cursor.execute(f"PRAGMA table_info({self.table});").fetchall()
        df_columns = self.create_meta_data()

        for i in range(len(df_columns)):
            for j in range(len(db_columns)):
                if df_columns[i][0] == db_columns[j][1] and df_columns[i][1] == db_columns[j][2]:
                    break
                if j == len(db_columns) - 1:
                    self.add_column(df_columns[i][0] + " " + df_columns[i][1])

    def insert_rows(self):
        """"""
        self.verify_column_persistence()
        table_info = self.dataframe.columns.values.tolist()

        values = "? , " * len(table_info)
        columns = ", ".join(table_info)

        data = self.dataframe.to_records(index=False).tolist()
        self.cursor.executemany(f"""INSERT INTO {self.table} ({columns}) VALUES({values[:-2]});""", data, )
        self.conn.commit()

    def find_similar_columns(self):
        """"""
        column_names = self.dataframe.columns.values.tolist()
        starts_with = []
        for i in column_names:
            first_word = str(i).split("_")[0]
            counter = 0
            for j in column_names:
                if first_word == str(j).split("_")[0]:
                    counter += 1
            if counter > 2 and first_word not in starts_with and first_word != "is":
                starts_with.append(first_word)
        return starts_with

    def create_dependency_tables(self):
        """"""
        similar_columns = self.find_similar_columns()
        for i in similar_columns:
            temp_df = self.dataframe.loc[:, self.dataframe.columns.str.startswith(i)]
            db = DatabasePipe(table=i, dataframe=temp_df)
            db.create_table()
            db.insert_rows()

            db_columns = self.cursor.execute(f"PRAGMA table_info({i});").fetchall()
            for column in range(len(db_columns)):
                if db_columns[column][5] == 1:
                    column_name = db_columns[column][1]
                    # self.dataframe.insert(column=column_name , value=)
                    break

            columns_to_drop = self.dataframe.loc[:, self.dataframe.columns.str.startswith(i)].columns.values.tolist()
            self.dataframe.drop(labels=columns_to_drop, axis='columns', inplace=True)
