import sqlite3
import os, json
from modules import utility, schema_handler

class SQLHandler():
    def __init__(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
        if not os.path.exists(os.path.join(db_path, "sqlite")):
            os.makedirs(os.path.join(db_path, "sqlite"))
        db_path = os.path.join(db_path, "sqlite", "database.db")

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS _schemas(collection_name TEXT, schema_structure TEXT);")

        self.schema_handler = schema_handler.SchemaHandler(self)

    def upload_sql(self, data: dict, filename: str):
        sql_skeleton = self.schema_handler.generate_schema(data)
        table_name = self.schema_handler.existing_schema_sql(sql_skeleton)

        if table_name == None:
            print("table doesnt exist")
            table_name = self.schema_to_table(filename, sql_skeleton)
            self.schema_handler.upload_schema_sql(table_name=table_name, generated_schema=sql_skeleton)
            print("Made new Schema")
        
        print(f"Entry to be Saved in {table_name}")
        
        if isinstance(data, dict):
            print("File is a single object. Inserting 1 document...")
            id = utility.random_id_generator(8)
            properties_string = utility.clean_list_to_str(data.keys())
            print(properties_string.split(", "))
            values_string = utility.clean_values_to_str(data, properties_string.split(", "))

            self.cursor.execute(f"INSERT INTO {table_name}({properties_string}) VALUES({values_string});")
            print(f"Successfully inserted document with ID: {id}")

    def schema_to_table(self, file_name: str, json_object: dict):
        properties = json_object["properties"]
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
        
        table_names = self.list_tables()
        table_name = utility.get_unduplicated_name(options=table_names, file_name=file_name, separate_extension=True)

        self.cursor.execute(f'INSERT INTO _schemas(collection_name, schema_structure) VALUES("{table_name}", "{json_object}");')

        self.create_table(name=table_name, cols=columns)

        return table_name

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

    # def upload_object_to_table(self, json_object: dict, table_name: str):
    #     properties = json_object.keys()
    #     values = []
    #     for property in properties:
    #         values.append(json_object[property])

    #     self.cursor.execute(f"INSERT INTO {table_name}({", ".join(properties)}) VALUES({", ".join(values)});")
    
    def list_tables(self):
        return self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

    
    def get_table_dir(self):
        title = "SQL Tables"
        inc_list = self.list_tables()
        up_list = []
        for table in inc_list:
            element = {
                "title": table,
                "url": f"/sql/{table}"
            }
            up_list.append(element)
        return {
            "title": title,
            "list": up_list
        }

# a = SQLHandler()

# a.cursor.execute("DROP TABLE identify_me_pleasesql")