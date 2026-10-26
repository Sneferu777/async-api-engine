import os, csv
import sqlite3

class CSVSink:
    def __init__(self, filepath : str, fieldnames : list) : 
        self.filepath = filepath
        self.fieldnames = fieldnames
        self._file = None 
        self._writer = None

    def open(self) : 
        file_exists = os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0

        self._file = open(filepath, mode="a", buffering=1 , newline="", encoding="UTF-8")
        self._writer = csv.DicWriter(self._file, fieldnames=self.fieldnames)

        if not file_exists :
            self._writer.writeheader()

    def write_row(self, record : dict):
        self._writer.write_row(record)

    def close(self) : 
        if self._file : 
            self._file.close()



class SQLSink:

    def __init__(self, db_path : str):
        self.db_path = db_path 

    def init_schema(self) : 

        with sqlite3.connect(self.db_path) as conn : 
            cursor = conn.cursor()
            cursor.execute("""
    
                CREATE TABLE IF NOT EXISTS quotes (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author TEXT,
                    quote TEXT
                )

                           """)
            cursor.commit()


    def write_batch(self, records : dict) : 

        tuples = [(r.get("author"), r.get("quote")) for r in records]

        query = "INSERT INTO quotes (author, quote) VALUES(?,?)"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, tuples)
            cursor.commit()

