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
            image = preprocessor.fill_transparent_with_white(preprocessor.bytestream_to_img(file_bytes))
            predictions = classifier.classify(image)
        elif type.mime.startswith("video/"):
            frames = preprocessor.get_video_frames(file_bytes, 5)
            predictions = []
            for frame in frames:
                predictions.append(classifier.classify(preprocessor.fill_transparent_with_white(frame)))
            predictions = avg_predictions(predictions)
        else:
            raise ValueError("Invalid file type. File must be either an image or a video.")
        
    file_id = bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={"keywords": predictions})
    return (file_id, predictions[0])


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

def index_file_to_fs():
    pass