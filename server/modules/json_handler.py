from modules import schema_handler

class JSONHandler():
    def __init__(self, db):
        self.db = db
        self.schema_handler = schema_handler.SchemaHandler(db)

    def get_json_by_query(self, query):
        pass

    def get_json_storage(self, collection):
        collection_content = self.db[collection].find({})
        json_storage_list:list = []
        for obj in collection_content:
            json_storage_list.append(self.get_shallow_copy(collection_obj=obj))
        return json_storage_list
    
    def upload_json(self, data: dict, filename: str):
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