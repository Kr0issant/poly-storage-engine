from fastapi import FastAPI, HTTPException, UploadFile, Request, Form, File
from fastapi.middleware.cors import CORSMiddleware
from server.modules import database as database
from modules.search import Search

app = FastAPI()
db = database.Database()
search = Search()

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
        file_info = await db.upload(file_name=file.filename, file_bytes=file_bytes, classify=True)
        print(f"uploaded file: {file_info}")
    return {"status": "completed"}

@app.get("/explorer/{type}/{category}/{subcategory}/{id}")
async def fetch_item(type:str, category:str, subcategory:str, id:str):
    return db.get_dir([type, category,subcategory,id])
@app.get("/explorer/{type}/{category}/{subcategory}")
async def fetch_subcat(type:str, category:str, subcategory:str):
    return db.get_dir([type, category,subcategory])
@app.get("/explorer/{type}/{category}")
async def fetch_cat(type:str, category:str):
    return db.get_dir([type, category])
@app.get("/explorer/{type}")
async def fetch_type(type:str):
    return db.get_dir([type])

@app.get("/search?query={query}")
async def fetch_query(query:str):
    query_list = search.get_keywords_from_query(query=query)
    search_results = db.get_results_from_keywords(query_list)
    search_results = search.sort_by_score(search_results, query_list)
    return search.shorten_data(search_results, query)

@app.get("/search/{id}")
async def fetch_item_by_id(id:str):
    db.get_file(id)