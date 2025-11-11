from pymongo import MongoClient
from bson.objectid import ObjectId
from modules import preprocessor, classifier
import gridfs, filetype, json

client = MongoClient("mongodb://localhost:27017/")

db = client["test"]

bucket = gridfs.GridFSBucket(db)

filesystem = dict()

def upload_sync(file_name: str, file_bytes: bytes, classify: bool = False):
    if classify:
        type = filetype.guess(file_bytes)
        if type is None:
            print(f"Error: Invalid file {file_name}")
            return
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
            print(f"Error: Invalid file type {file_name}")
            return
        
    file_id = bucket.upload_from_stream(filename=file_name, source=file_bytes, metadata={"keywords": predictions})
    add_file(file_id, predictions[0]["label"])

    print(f"Successfully processed and uploaded: {file_name}, ID: {file_id}")
    return (file_id, predictions[0])

def process_files_batch(task_id: str, files_data: list, task_store: dict):
    total = len(files_data)
    task_store[task_id]["status"] = "processing"

    try:
        for (file_name, file_bytes) in files_data:
            task_store[task_id]["current_file"] = file_name
            upload_sync(file_name=file_name, file_bytes=file_bytes, classify=True)
            task_store[task_id]["processed_files"] += 1
        
        task_store[task_id]["status"] = "complete"
        task_store[task_id]["current_file"] = ""
        
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        task_store[task_id]["status"] = "error"
        task_store[task_id]["error_message"] = str(e)

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

def sync_filesystem():
    with open("modules/classification.json", "r") as data:
        categories = json.load(data)

    for file in bucket.find({}):
        label = file["metadata"]["keywords"][0]
        category = categories[label]
        id = file["_id"]
        
        if category not in filesystem:
            filesystem[category] = dict()
        if label not in filesystem[category]:
            filesystem[category][label] = []
        if id not in filesystem[category][label]:
            filesystem[category][label].append(id)

    return filesystem

def add_file(id: ObjectId, label: str):
    with open("modules/classification.json", "r") as data:
        categories = json.load(data)

    category = categories[label]

    if category not in filesystem:
        filesystem[category] = dict()
    if label not in filesystem[category]:
        filesystem[category][label] = []
    if id not in filesystem[category][label]:
        filesystem[category][label].append(id)

    return filesystem

def delete_file(id: ObjectId):
    with open("modules/classification.json", "r") as data:
        categories = json.load(data)

    for file in bucket.find({"_id": id}):
        label = file["metadata"]["keywords"][0]
        category = categories[label]

    bucket.delete(id)

    filesystem[category][label].remove(id)
    if (len(filesystem[category][label]) == 0):
        del filesystem[category][label]
    if (len(filesystem[category].keys()) == 0):
        del filesystem[category]

    return filesystem

def rename_file(id: ObjectId, new_name: str):
    bucket.rename(id, new_name)
    return