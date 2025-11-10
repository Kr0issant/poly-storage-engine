from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
from modules import preprocessor, classifier
import filetype

client = MongoClient("mongodb://localhost:27017/")

db = client["test"]

bucket = gridfs.GridFSBucket(db)

async def upload(file_name: str, file_bytes: bytes, classify: bool = False):
    if classify:
        type = filetype.guess(file_bytes)
        if type is None:
            raise ValueError("Invalid file.")
        elif type.mime.startswith("image/"):
            print("image")
            image = preprocessor.fill_transparent_with_white(preprocessor.bytestream_to_img(file_bytes))
            predictions = classifier.classify(image)
        elif type.mime.startswith("video/"):
            print("video")
            frames = preprocessor.get_video_frames(file_bytes, 5)
            predictions = []
            for frame in frames:
                predictions.append(classifier.classify(preprocessor.fill_transparent_with_white(frame)))
        else:
            raise ValueError("Invalid file type. File must be either an image or a video.")
        
    print(predictions)
    file_id = bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={"keywords": ["script", "python"]})
    return file_id