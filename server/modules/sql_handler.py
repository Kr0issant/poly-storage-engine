import sqlite3
import os, json

class SQLHandler():
    def __init__(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sqlite", "database.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, name: str, cols):
        details = ""
        for entry in cols:
            for i, col in enumerate(entry):
                if i == 0:
                    col = f'"{col}"'
                details += col + " "
            details = details.strip() + ", "

        query = f"CREATE TABLE {name}({details.strip()[:-1]});"
        # print(query)
        self.cursor.execute(query)

    def schema_to_table(jsonObject):
        data = json.load(jsonObject)
        

    def upload_sql_to_db(jsonObject):
        pass
    

# a = SQLHandler()

# a.create_table("tablename", ["ID", "INT", "PRIMARY KEY"], ["NAME", "VARCHAR(50)", "NOT NULL"], ["AGE", "INT"])