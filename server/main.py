from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from modules import database
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
        database.process_files_batch,
        task_id = task_id,
        files_data = files_data,
        task_store = upload_tasks
    )

    return {"task_id": task_id}

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    task = upload_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task