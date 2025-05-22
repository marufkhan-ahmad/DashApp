# src/database/data.py

import pyodbc
from src.pipeline.exception import CustomException

class Database:
    def __init__(self):
        # SQL Server connection details
        self.server = r'LAPTOP-CN6IDNLC\SQLEXPRESS'
        self.database = 'Flipshope'
        self.conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
        )

    def fetch_data(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Hyyzo")
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
        
        # Convert rows to tuples (just in case they are single-element)
            data = [tuple(row) for row in data]

            cursor.close()
            conn.close()
            return columns, data
        except Exception as e:
            raise CustomException(f"SQL Server error: {str(e)}")

