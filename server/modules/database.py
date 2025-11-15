from pymongo import MongoClient
from bson.objectid import ObjectId
from modules import preprocessor, classifier, json_handler, file_handler, schema_handler
import gridfs, filetype, json
from modules import utility


class Database(): # Maine Storage Class
    def __init__(self, mongo_uri = "mongodb://localhost:27017/", db_name = "test1"):
        #Connect to Mongo DB and Setup Database and GridFS for Files
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.bucket = gridfs.GridFSBucket(self.db)

        self.files = file_handler.FileHandler(self.db, self.bucket)
        self.schemas = schema_handler.SchemaHandler(self.db)
        self.jsons  = json_handler.JSONHandler(self.db)

        with open("modules/classification.json", "r") as file:
            self.categories: list = json.load(file)


    
    def upload_sync(self, file_name: str, file_bytes: bytes, classify: bool = False):
        if not classify:
            return
        # Trying to Load JSON First
        try:
            data = json.loads(file_bytes.decode('utf-8'))
            # schema = self.schemas.generate_schema(data)
            print("Detected JSON")
            json_type = self.schemas.get_json_structure_type(data)
            print("Structure got" + json_type)
            
            if json_type == "json-native": # Json found Deep, Uploading to MongoDB
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                        print("upload start")
                        self.jsons.upload_json(data = item, filename=file_name)
                        print("upload end")
                
            if json_type == "sql-candidate":
                if isinstance(data,dict):
                    data = [data]
                for item in data:
                    print(self.schemas.generate_schema(item))

            return
        
        except Exception:
            print("Not a Json File, Processing as a binary File ")

        # If JSON not Found Its Cnsidered a File
        type = filetype.guess(file_bytes)
        if type is None: # for wrong formats/ corrupt files
            print(f"Error: Invalid file {file_name}")
            return
        elif type.mime.startswith("image/"): # Images
            type = "image"
            image = preprocessor.fill_transparent_with_white(preprocessor.bytestream_to_img(file_bytes))
            predictions = classifier.classify(image)
        elif type.mime.startswith("video/"): # Videos
            type = "video"
            frames = preprocessor.get_video_frames(file_bytes, 5)
            predictions = []
            for frame in frames:
                predictions.append(classifier.classify(preprocessor.fill_transparent_with_white(frame)))
            predictions = utility.avg_predictions(predictions)
        else: # Some Other (Just in Case)
            print(f"Error: Invalid file type {file_name}")
            return

        metadata = {
            "keywords": predictions,
            "category": self.categories[predictions[0]["label"]], 
            "subcategory": predictions[0]["label"],
            "type": type
        }    
        file_id = self.files.upload_file(file_name, file_bytes, metadata)    # File Handler Uploads the file to Database

        print(f"Successfully processed and uploaded: {file_name}, ID: {file_id}")
        return (file_id, predictions[0])

    def process_files_batch(self, task_id: str, files_data: list, task_store: dict):
        task_store[task_id]["status"] = "processing"

        try:
            for (file_name, file_bytes) in files_data:
                task_store[task_id]["current_file"] = file_name
                self.upload_sync(file_name=file_name, file_bytes=file_bytes, classify=True)
                task_store[task_id]["processed_files"] += 1
            
            task_store[task_id]["status"] = "complete"
            task_store[task_id]["current_file"] = ""

        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            task_store[task_id]["status"] = "error"
            task_store[task_id]["error_message"] = str(e)

 