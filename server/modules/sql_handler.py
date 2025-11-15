import sqlite3
import os, json
import utility

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

    def schema_to_table(self, jsonObject):
        properties = json.load(jsonObject)["properties"]
        id_duplicates = 0
        columns = []
        for property_name in properties.keys():
            if property_name == ("_" * id_duplicates) + "ID":
                id_duplicates += 1

            type = properties[property_name]["type"]
            match type:
                case "string":
                    type = "TEXT"
                case "integer":
                    type = "INT"
                case "boolean":
                    type = "INT"
                case "number":
                    type = "FLOAT"
                case _:
                    type = "TEXT"

            columns.append([property_name, type])

        columns.insert(0, [("_" * id_duplicates) + "ID", "TEXT", "PRIMARY KEY"])
        self.create_table(columns)

    def upload_sql_to_db(self, jsonObject):
        pass

# a = SQLHandler()

# a.create_table("tablename", ["ID", "INT", "PRIMARY KEY"], ["NAME", "VARCHAR(50)", "NOT NULL"], ["AGE", "INT"])