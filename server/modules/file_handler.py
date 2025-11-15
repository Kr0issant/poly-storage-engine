from bson import ObjectId
import re
class FileHandler:
    def __init__(self, db, bucket):
        self.db = db
        self.bucket = bucket
        self.fs_files = self.db.fs.files
        #Create Indices for File Manager and Search
        self.assign_indices()
        pass
    
    def get_file_filters(self):
        self.fs_files
    
    def assign_indices(self):
        # Indices for File Manager
        self.fs_files.create_index([
            ("metadata.category", 1), 
            ("metadata.subcategory", 1)
        ])

        #Indices for Search through Keywords
        self.fs_files.create_index("metadata.keywords['labels']")
    
    def upload_file(self, file_name, file_bytes, metadata):
        file_id = self.bucket.upload_from_stream(
            filename=file_name, 
            source=file_bytes, 
            metadata=metadata
        )
        print(f"Uploaded file {file_name} to GridFS. ID: {file_id}")
        return file_id

    def get_file(self, id: str):
        return self.fs_files.find_one({"_id": ObjectId(id)})
        
    def get_dir(self, type:list):
        directory_title = []
        directory_list = []
        
        if len(type) == 3:         #IDs
            file_doc = self.get_file(ObjectId(type[2]))
            file_doc["_id"] = str(file_doc["_id"])
            directory_title = file_doc["filename"]
            directory_list = [{"id": file_doc["_id"], "type": file_doc["metadata"]["type"]}]
            
        elif len(type) == 2:       #Subcategory
            directory_title = type[1]
            search_results = self.fs_files.find({
                "metadata.category": type[0],
                "metadata.subcategory": type[1].replace("_", " ")
            })
            for result in search_results:
                element = {
                    "title": result["filename"],
                    "url": f"media/{type[0]}/{type[1].replace(" ", "_")}/{str(result["_id"])}",
                    "type": result["metadata"]["type"]
                }
                directory_list.append(element)
            

        elif len(type) == 1:       #Category
            directory_title = type[0]
            search_results = self.fs_files.distinct("metadata.subcategory", {"metadata.category": type[0]})
            for result in search_results:
                element = {
                    "title":result,
                    "url": f"media/{type[0]}/{result.replace(" ", "_")}",
                    "type": "folder"
                }
                
                directory_list.append(element)

        elif len(type) == 0:      #Media
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
        print(keywords, "hello")
        h = list(self.fs_files.find())
        output_list = []
        for x in h:
            normalized_keywords = self.get_corrected_keyword_list(x["metadata"]["keywords"])
            for search_kw in keywords:
                pattern = re.compile(re.escape(search_kw), re.IGNORECASE)
                

                # Check if any normalized keyword matches the pattern
                if any(pattern.search(nk) for nk in normalized_keywords):
                    output_list.append(x)
                    break 

        return output_list
    
    def rename_file(self, id: ObjectId, new_name: str):
        self.bucket.rename(id, new_name)
        return
    
    def delete_file(self, id: ObjectId):
        self.bucket.delete(id)
        return
    def get_corrected_keyword_list(self, keyword_list:list):
        keywords = []
        for key in keyword_list:
            keywords.append(key["label"])
        return keywords