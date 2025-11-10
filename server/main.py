from fastapi import FastAPI, HTTPException, UploadFile, Request, Form, File
from fastapi.middleware.cors import CORSMiddleware
from modules import database

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

@app.get("/")
def root():
    return {"greeting": "Hello, useless customer"}

@app.post("/upload")
async def upload_media(files: list[UploadFile] = File(...)):
    for file in files:
        file_bytes: bytes = await file.read()
        file_info = await database.upload(file_name=file.filename, file_bytes=file_bytes, classify=True)
        print(f"uploaded file: {file_info}")