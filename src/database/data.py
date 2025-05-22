# src/database/data.py

from dotenv import load_dotenv
import os
import pyodbc
from src.pipeline.exception import CustomException

class Database:
    def __init__(self):
        load_dotenv()

        self.driver = os.getenv("DB_DRIVER")
        self.server = os.getenv("DB_SERVER")
        self.database = os.getenv("DB_NAME")
        self.conn_str = (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
        )


    def fetch_data(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Hyyzo")
            columns = [column[0] for column in cursor.description]
            data = [list(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return columns, data
        except Exception as e:
            raise CustomException(f"SQL Server error: {str(e)}")

