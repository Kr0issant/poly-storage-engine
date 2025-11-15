import json
import genson

class SchemaHandler:
    def __init__(self, db):
        self.db = db
        
    def existing_schema_nosql(self, incoming_schema):     
        canon_schema_string = self._get_canonical_schema_str(incoming_schema)
        
        collection = self.db.schemas
        existing_schema_doc = collection.find_one({"schema_structure": canon_schema_string})
        print(f"DEBUG: find_one result: {existing_schema_doc}")

        if existing_schema_doc:
            print("found existing schema")
            return existing_schema_doc['collection_name']
        else:
            return None
    
    def existing_schema_sql(self, incoming_schema):
        canon_schema_string = self._get_canonical_schema_str(incoming_schema)

        tables = self.db.cursor.execute(f"SELECT collection_name FROM _schemas WHERE schema_structure={canon_schema_string}").fetchall()

        if len(tables) == 0:
            return None
        else:
            return tables[0]
    
    def upload_schema(self,collection_name: str, generated_schema:dict):
        canon_schema_string = self._get_canonical_schema_str(generated_schema)

        schema_doc = {
            "collection_name": collection_name,
            "schema_structure": canon_schema_string
        }
        print("Schema Made")
        result = self.db["schemas"].insert_one(schema_doc)
        print("Schema Uploaded" )
        return result
    
    def upload_schema_sql(self, table_name: str, generated_schema: dict):
        canon_schema_string = self._get_canonical_schema_str(generated_schema)

        self.db.cursor.execute(f"INSERT INTO _schemas(collection_name, schema_structure) VALUES({table_name}, {canon_schema_string});")
        print("Schema Uploaded")
        return 

    def generate_schema(self, obj):
        builder = genson.SchemaBuilder()

        if isinstance(obj, list):
            for item in obj:
                builder.add_object(item)
        else:
             builder.add_object(obj)
        
        # 3. Get the final schema dictionary
        generated_schema = builder.to_schema()
        
        print("  [Genson]: Blueprint generated successfully.")
        return generated_schema
    
    def _get_canonical_schema_str(self, schema_dict: dict) -> str:

            if not isinstance(schema_dict, dict):
                return "{}"
            return json.dumps(schema_dict, sort_keys=True)



    def is_obj_flat(self, obj) -> bool:
        if not isinstance(obj, dict):
            return False
        for value in obj.values():
            if isinstance(value, (dict, list)):
                return False
        return True 

    def get_json_structure_type(self, data) -> str:
        if self.is_obj_flat(data):
            return "sql-candidate"

        if isinstance(data, list):
            if not data:
                return "json-native"
            # Check if ALL items in the list are flat objects
            if all(self.is_obj_flat(item) for item in data):
                return "sql-candidate"

        return "json-native"
