from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from modules import database, json_handler, file_handler
from bson.objectid import ObjectId
from modules.search import Search
import uuid


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5500",  
    "http://127.0.0.1:5500" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

upload_tasks = dict()

db = database.Database()
files:file_handler.FileHandler = db.files
jsons:json_handler.JSONHandler = db.jsons

search = Search()

@app.get("/")
def root():
    return {"greeting": "Hello, useless customer"}

@app.post("/upload")
async def upload_media(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)):
    task_id = str(uuid.uuid4())

    files_data = []
    for file in files:
        files_data.append((file.filename, await file.read()))
        
    upload_tasks[task_id] = {
        "status": "pending",
        "total_files": len(files_data),
        "processed_files": 0,
        "current_file": ""
    }

    background_tasks.add_task(
        db.process_files_batch,
        task_id = task_id,
        files_data = files_data,
        task_store = upload_tasks
    )

    return {"task_id": task_id}

# Progress Tracking
@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    task = upload_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] == "complete" or task["status"] == "error":
        return upload_tasks.pop(task_id)
    else:
        return task

# Media Explorer
@app.get("/explorer/media")
async def fetch_type():
    return files.get_dir([])

@app.get("/explorer/media/{category}")
async def fetch_cat(category: str):
    return files.get_dir([category])

@app.get("/explorer/media/{category}/{subcategory}")
async def fetch_subcat(category: str, subcategory: str):
    return files.get_dir([category, subcategory])

@app.get("/explorer/media/{category}/{subcategory}/{id}")
async def fetch_item(category: str, subcategory:str, id: str):
    item_details =  files.get_dir([category, subcategory, id])
    item_details["list"][0]["stream_url"] = f"media-stream/{id}"

    return item_details


# NoSQL Explorer
@app.get("/explorer/nosql")
async def get_collections():
    print({"list": db.db.list_collection_names()})
    return {"list": db.db.list_collection_names()}
    
@app.get("/explorer/nosql/{collection}")
async def get_json_path(collection:str):
    return jsons.get_json_storage(collection=collection)


# SQL Explorer



# File Operations
@app.get("/delete/{id}")
async def delete_file(id: str):
    files.delete_file(ObjectId(id))
    return


# Searching
@app.get("/search")
async def fetch_query(query:str):
    query_list = search.get_keywords_from_query(query=query)
    search_results = files.get_results_from_keywords(query_list)
    search_results = search.sort_by_score(search_results, query_list)
    return search.shorten_data(search_results, query)

@app.get("/fetch-id/{id}")
async def fetch_item_by_id(id:str):
    files.get_file(id)


# Media Streaming
@app.get("/media-stream/{file_id}")
async def stream_media_file(file_id: str, request: Request):
    try:
        object_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid File ID Format")
    
    metadata = files.get_file(object_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    content_type = metadata.get("metadata", {}).get("type", "application/octet-stream")

    # Images
    if content_type == "image":
        stream = db.bucket.open_download_stream(object_id)
        if stream:
            return Response(content=stream.read(), media_type=f"image/{metadata['filename'].split('.')[-1]}")
        else:
            raise HTTPException(status_code=500, detail="Could not open image stream")
    
    # Videos
    elif content_type == "video":
        file_size = metadata["length"]
        range_header = request.headers.get("range")

        file_extension = files.get_file(object_id)["filename"].split(".")[-1]

        if range_header:
            try:
                byte1, byte2 = range_header.replace("bytes=", "").split("-")
                start = int(byte1)
                end = int(byte2) if byte2 else file_size - 1
            except ValueError:
                raise HTTPException(status_code=416, detail="Invalid Range header")
            
            chunk_size = end - start + 1

            def file_generator(start, end):
                with db.bucket.open_download_stream(object_id) as stream:
                    stream.seek(start)
                    while True:
                        chunk = stream.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            
            headers = {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(chunk_size),
                'Content-Type': f'video/{file_extension}'
            }
            return StreamingResponse(file_generator(start, end), status_code=206, headers=headers)

        else:
            def file_generator_full():
                with db.bucket.open_download_stream(object_id) as stream:
                    yield from stream

            headers = {
                'Content-Type': f'video/{file_extension}',
                'Content-Length': str(file_size)
            }
            return StreamingResponse(file_generator_full(), headers=headers)
        
    raise HTTPException(status_code=415, detail="Unsupported media type for streaming")