from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from modules import database, json_handler
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
json_db = json_handler.JSONHandler()
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

# Explorer
@app.get("/explorer/{type}")
async def fetch_type(type: str):
    return db.get_dir([type])

@app.get("/explorer/{type}/{category}")
async def fetch_cat(type: str, category: str):
    return db.get_dir([type, category])

@app.get("/explorer/{type}/{category}/{subcategory}")
async def fetch_subcat(type: str, category: str, subcategory: str):
    return db.get_dir([type, category, subcategory])

@app.get("/explorer/{type}/{category}/{subcategory}/{id}")
async def fetch_item(type: str, category: str, subcategory:str, id: str):
    return db.get_dir([type, category, subcategory, id])

# Searching
@app.get("/search")
async def fetch_query(query:str):
    query_list = search.get_keywords_from_query(query=query)
    search_results = db.get_results_from_keywords(query_list)
    search_results = search.sort_by_score(search_results, query_list)
    return search.shorten_data(search_results, query)

@app.get("/fetch-id/{id}")
async def fetch_item_by_id(id:str):
    db.get_file(id)

@app.get("/explorer/json/{path}")
async def get_json_path(path:str):
    # json_db
    pass