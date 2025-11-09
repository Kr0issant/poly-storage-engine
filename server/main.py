from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"Hello":"World"}

# @app.post("/upload/media")
# def upload_media(file):
