import sqlite3
import os, json
from modules import utility

class SQLHandler():
    def __init__(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
        if not os.path.exists(os.path.join(db_path, "sqlite")):
            os.makedirs(os.path.join(db_path, "sqlite"))

        self.conn = sqlite3.connect(os.path.join(db_path, "sqlite", "database.db"))
        self.cursor = self.conn.cursor()

    def upload_sql(self, data: dict, filename: str):
        json_skeleton = self.schema_handler.generate_schema(data)
        collection_name = self.schema_handler.existing_schema(json_skeleton)

        if collection_name == None:
            self.schema_handler.upload_schema(collection_name=filename, generated_schema=json_skeleton)
            print("Making new Schema")
            collection_name = filename
        
        collection = self.db[collection_name]
        print(f"File to be Saved in {collection_name}")
        
        if isinstance(data, dict):
            print("File is a single object. Inserting 1 document...")
            result = collection.insert_one(data)
            print(f"Successfully inserted document with ID: {result.inserted_id}")

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

    def schema_to_table(self, file_name: str, json_object: dict):
        properties = json.load(json_object)["properties"]
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
        
        table_names = self.cursor.execute("SELECT name FROM database WHERE type='table';").fetchall()
        table_name = utility.get_unduplicated_name(options=table_names, file_name=file_name, separate_extension=True)

        self.create_table(name=table_name, cols=columns)

        return table_name

    def upload_object_to_table(self, json_object: dict, table_name: str):
        properties = json_object.keys()
        values = []
        for property in properties:
            values.append(json_object[property])

        self.cursor.execute(f"INSERT INTO {table_name}({", ".join(properties)}) VALUES({", ".join(values)});")
    

# a = SQLHandler()

# a.create_table("tablename", ["ID", "INT", "PRIMARY KEY"], ["NAME", "VARCHAR(50)", "NOT NULL"], ["AGE", "INT"])