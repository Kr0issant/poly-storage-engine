from pymongo import MongoClient
from bson.objectid import ObjectId
from modules import preprocessor, classifier
import gridfs, filetype, json

class Database():
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["test"]
        self.bucket = gridfs.GridFSBucket(self.db)

        self.categories:list
        with open("modules/classification.json", "r") as file:
            self.categories = json.load(file)

        self.fs_files = self.db.fs.files
        self.assign_indices()
        pass
    
    def upload_sync(self, file_name: str, file_bytes: bytes, classify: bool = False):
        if classify:
            type = filetype.guess(file_bytes)
            if type is None:
                print(f"Error: Invalid file {file_name}")
                return
            elif type.mime.startswith("image/"):
                type = "image"
                image = preprocessor.fill_transparent_with_white(preprocessor.bytestream_to_img(file_bytes))
                predictions = classifier.classify(image)
            elif type.mime.startswith("video/"):
                type = "video"
                frames = preprocessor.get_video_frames(file_bytes, 5)
                predictions = []
                for frame in frames:
                    predictions.append(classifier.classify(preprocessor.fill_transparent_with_white(frame)))
                predictions = avg_predictions(predictions)
            else:
                print(f"Error: Invalid file type {file_name}")
                return
            
        file_id = self.bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={
            "keywords": predictions,
            "category": self.categories[predictions[0]["label"]], 
            "subcategory": predictions[0]["label"],
            "type": type
        })

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

    def assign_indices(self):
        self.fs_files.create_index([
            ("metadata.category", 1), 
            ("metadata.subcategory", 1)
        ])
        self.fs_files.create_index("metadata.keywords['labels']")

    def get_file(self, id: ObjectId):
        self.fs_files.find("_id"==id)
        pass
    
    def get_dir(self, type:list):
        directory_title = []
        directory_list = []
        
        if len(type) == 4:         #IDs
            directory_title = self.get_file(ObjectId(type[3]))["filename"]
            directory_list =  self.get_file(ObjectId(type[3]))
            
        elif len(type) == 3:       #Subcategory
            directory_title = type[2]
            search_results = self.fs_files.find({
                "metadata.category": type[1],
                "metadata.subcategory": type[2]
            })
            for result in search_results:
                element = {
                    "title": result["filename"],
                    "url": f"media/{type[1]}/{type[2]}/{str(result["_id"])}",
                    "type": result["metadata"]["type"]
                }
                directory_list.append(element)
            

        elif len(type) == 2:       #Category
            directory_title = type[1]
            search_results = self.fs_files.distinct("metadata.subcategory", {"metadata.category": type[1]})
            for result in search_results:
                element = {
                    "title":result,
                    "url": f"media/{type[1]}/{result}",
                    "type": "folder"
                }
                
                directory_list.append(element)

        elif len(type) == 1 and type[0]=="media":      #Media
            directory_title = "media"
            search_results = self.fs_files.distinct("metadata.category")
            for result in search_results:
                element = {
                    "title":result,
                    "url": f"media/{result}",
                    "type": "folder"
                }
                
                directory_list.append(element)
        
        return {
            "title":directory_title,
            "list":directory_list,
        }
    
    def get_results_from_keywords(self, keywords:list):
        search_results = self.fs_files.find({
            "metadata.keywords":{
                "$in":keywords
            }
        })
        return search_results

    def rename_file(self, id: ObjectId, new_name: str):
        self.bucket.rename(id, new_name)
        return
    
    def delete_file(self, id: ObjectId):
        self.bucket.delete(id)
        return
    
    # JSON
    def upload_schema(self,collection_name, generated_schema:dict):
        if self.existing_schema == None:
            schema_doc = {
                "collection_name": collection_name,
                "schema_stucture": generated_schema
            }
            result = self.db["schemas"].insert_one(schema_doc)
            return result

    def existing_schema(self, incoming_schema):
        existing_schema_doc = self.db.schemas.find_one({
            "schema_structure": incoming_schema
        })
        if existing_schema_doc:
            collection_name = existing_schema_doc['collection_name']
            return collection_name

        else:
            return None
    
def avg_predictions(predictions):
    category_scores = dict()
    size = len(predictions)
    for i in range(len(predictions)):
        for j in predictions[i]:
            label = j["label"]
            score = j["score"]
            
            category_scores[label] = category_scores.get(label, 0.0) + score

    avg_p = []
    for label, total_score in category_scores.items():
        average_score = total_score / size
        avg_p.append({"label": label, "score": average_score})

    avg_p = sorted(
        avg_p, 
        key=lambda d: d["score"], 
        reverse=True
    )
    return avg_p[:3]