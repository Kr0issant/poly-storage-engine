from modules import schema_handler, utility
import json

class JSONHandler():
    def __init__(self, db):
        self.db = db
        self.schema_handler = schema_handler.SchemaHandler(db)

    def get_json_by_query(self, query_objects, collection_name):
        #
        self.db[collection_name].find()
        pass

    def get_collection_dir(self):
        title = "Json Collections"
        inc_list = self.db.list_collection_names()
        up_list = []
        for collection in inc_list:
            if not collection in ["fs.chunks", "fs.files","_schemas"]:
                element = {
                    "title": collection,
                    "url": f"nosql/{collection}",
                    "type": "collection"
                }
                up_list.append(element)
        
        return {
            "title": title,
            "list": up_list
        }

    def get_filters(self, collection_name):
        get_schema_for_collection = self.db["_schemas"].find_one({"collection_name":collection_name})
        schema_object = json.loads(get_schema_for_collection["schema_structure"])
        return schema_object
    

    def get_json_storage(self, collection):
        collection_content = list(self.db[collection].find())
        json_storage_list: list = []
        for obj in collection_content:
            element = self.get_shallow_copy(collection_obj=obj)
            _id = element["_id"]
            json_storage_list.append({
                "element":element,
                "url":f"nosql/{collection}/{_id}",
                "json_data": "collection"
            })
        return {
            "title": collection,
            "list": json_storage_list,
            "json_data": "collection"
        }
    
    def upload_json(self, data: dict, filename: str):
        json_skeleton = self.schema_handler.generate_schema(data)
        collection_name = self.schema_handler.existing_schema_nosql(json_skeleton)

        if collection_name == None:
            collection_name = utility.get_unduplicated_name(options=self.db.list_collection_names(), file_name="".join(filename.split(".")[:-1]))
            print("Making new Schema")
            self.schema_handler.upload_schema(collection_name=collection_name, generated_schema=json_skeleton)
        
        collection = self.db[collection_name]
        print(f"File to be Saved in {collection_name}")
        
        if isinstance(data, dict):
            print("File is a single object. Inserting 1 document...")
            result = collection.insert_one(data)
            print(f"Successfully inserted document with ID: {result.inserted_id}")
    
    def get_shallow_copy(self, collection_obj: dict):
        shallow_copy = dict()
        for key in collection_obj.keys():
            if key == "_id":
                shallow_copy[key] = str(collection_obj[key])
            else:
                if isinstance(collection_obj[key], list):
                    shallow_copy[key] = "List"
                elif isinstance(collection_obj[key], dict):
                    shallow_copy[key] = "Object"
                else:
                    shallow_copy[key] = collection_obj[key]
        return shallow_copy