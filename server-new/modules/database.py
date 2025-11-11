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
        with open("classification.json", "r") as file:
            self.categories = json.load(file)

        self.fs_files = self.db.fs.files
        self.assign_indices()
        pass
    
    def assign_indices(self):
        self.fs_files.create_index([
            ("metadata.category", 1), 
            ("metadata.subcategory", 1)
        ])
        self.fs_files.create_index("metadata.keywords['labels']")

    def get_file(self, id):
        self.fs_files.find("_id"==id)
        pass
    
    def get_dir(self, type:list):
        directory_title = []
        directory_list = []
        
        if type[3]:         #IDs
            directory_title = type[3]
            directory_list =  self.get_file(type[3])
            
        elif type[2]:       #Subcategory
            directory_title = type[2]
            search_results = self.fs_files.find({
                "metadata.category": type[1],
                "metadata.subcategory": type[2]
            })
            for result in search_results:
                element = {
                    "title":result['filename'],
                    "url": f"media/{type[1]}/{type[2]}/{result["_id"]}"
                }
                directory_list.append(element)

        elif type[1]:       #Category
            directory_title = type[1]
            search_results = self.fs_files.distinct("metadata.subcategory", {"metadata.category"==type[1]})
            for result in search_results:
                element = {
                    "title":result['filename'],
                    "url": f"media/{type[1]}/{result}"
                    }
                
                directory_list.append(element)

        elif type[0] and type[0]=="media":      #Media
            directory_title = "media"
            search_results = self.fs_files.distinct("metadata.category")
            for result in search_results:
                element = {
                    "title":result['filename'],
                    "url": f"media/{result}"
                    }
                
                directory_list.append(element)
        
        return {
                "title":directory_title,
                "list":directory_list
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
    
    async def upload(self, file_name: str, file_bytes: bytes, classify: bool = False):
        if classify:
            type = filetype.guess(file_bytes)
            if type is None:
                raise ValueError("Invalid file.")
            elif type.mime.startswith("image/"):
                image = preprocessor.fill_transparent_with_white(preprocessor.bytestream_to_img(file_bytes))
                predictions = classifier.classify(image)
            elif type.mime.startswith("video/"):
                frames = preprocessor.get_video_frames(file_bytes, 5)
                predictions = []
                for frame in frames:
                    predictions.append(classifier.classify(preprocessor.fill_transparent_with_white(frame)))
                predictions = self.avg_predictions(predictions)
            else:
                raise ValueError("Invalid file type. File must be either an image or a video.")
        
        file_id = Database.bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={
            "keywords": predictions, 
            "category":self.categories[predictions[0]["label"]], 
            "subcategory":predictions[0]["label"]
            })
        # add_file(file_id, predictions[0]["label"])
        return (file_id, predictions[0])
    
    def avg_predictions(self, predictions):
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