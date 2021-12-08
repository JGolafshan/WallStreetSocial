import os
import sqlite3


class DatabasePipe:
    """
    This class is used for the creation of an sqlite database/tables
    """

    def __init__(self):
        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.conn = sqlite3.connect(path + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()


class ModifyDatabase:
    def __init__(self, connection, table, dataframe):
        self.connection = connection
        self.table = table
        self.dataframe = dataframe

    def main_function(self):
        self.create_meta_data()
        self.create_table()
        self.insert_rows()

    def create_meta_data(self):
        self.dataframe = self.dataframe.convert_dtypes()
        self.dataframe = self.dataframe.select_dtypes(exclude=['object'])
        column_names = self.dataframe.columns.values.tolist()
        data_types = []

        for name in column_names:
            data_type = self.dataframe[name].dtypes.name
            if data_type == 'Int64':
                data_types.append('integer'.capitalize())
            else:
                data_types.append(str(self.dataframe[name].dtypes.name).capitalize())

        return [list(t) for t in zip(column_names, data_types)]

    def create_table(self):
        columns = ""
        meta_data = self.create_meta_data()
        for column in range(len(meta_data)):
            columns += meta_data[column][0] + " " + meta_data[column][1]
            if column != len(meta_data) - 1:
                columns += "," + "\n"

        self.connection.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} ({columns});""")
        self.connection.conn.commit()

    def add_column(self, meta_data):
        self.connection.cursor.execute(f"""ALTER TABLE {self.table}  ADD COLUMN {meta_data};""")
        self.connection.conn.commit()

    def set_primary_key(self):
        pass

    def verify_column_persistence(self):
        table_info = self.connection.cursor.execute(f"PRAGMA table_info({self.table});").fetchall()
        database_columns = []

        for column in range(len(table_info)):
            database_columns.append([table_info[column][1], table_info[column][2]])
        dataframe_columns = self.create_meta_data()

        for column_df in range(len(dataframe_columns)):
            for column_db in range(len(database_columns)):
                if dataframe_columns[column_df] == database_columns[column_db]:
                    break
                if column_db == len(table_info) - 1:
                    self.add_column(dataframe_columns[column_df][0] + " " + dataframe_columns[column_df][1])

    def insert_rows(self):
        self.verify_column_persistence()
        table_info = self.dataframe.columns.values.tolist()
        column_list = ""
        question_list = ""

        for column in range(len(table_info)):
            column_list += table_info[column]
            question_list += "?"
            if column != len(table_info) - 1:
                column_list += ", \n"
                question_list += ","

        data = self.dataframe.to_records(index=False).tolist()
        self.connection.cursor.executemany(f"""INSERT INTO {self.table} ({column_list}) VALUES({question_list});""",
                                           data, )
        self.connection.conn.commit()
