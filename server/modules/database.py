from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import filetype

client = MongoClient("mongodb://localhost:27017/")

db = client["test"]

bucket = gridfs.GridFSBucket(db)

async def upload(file_name: str, file_bytes: bytes, classify: bool = False):
    if classify:
        type = filetype.guess(file_bytes)
        if type is None:
            raise Exception
        elif type.mime.startswith("image/"):
            pass
        elif type.mime.startswith("video/"):
            pass
        else:
            raise Exception
        
    file_id = bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={"keywords": ["script", "python"]})
    return file_id