from fastapi import FastAPI, HTTPException, UploadFile, Request, Form, File
from db import mydb
import Items
import io
from PIL import Image
import model

app=FastAPI()
json_collection = mydb["json files"]


@app.get("/")
async def root():
    pass

@app.post("/jsons/")
def create_item(): # Json Item Creation
    item = Items.JSON(
        name="st",
        content={
            "name": "Aryan",
            "age": 18,
            "class": "student"
        }
    )

    result = json_collection.insert_one(item.model_dump())
    return {"id": str(result.inserted_id), "message": "Item stored"}

@app.get("/jsons/{name}")
def get_json(name:str):
    item = json_collection.find_one({"name":name})
    if not item:
        raise HTTPException(status_code=404, detail="Not Found")
    # item["id"] = str(item["_id"])
    return item

@app.post("/upload/")
async def handle_upload(imageUpload: UploadFile = File(...)):
    # request:Request
    # imageUpload: UploadFile = File(...) # Makes uploading the file required
    
    file_bytes: bytes = await imageUpload.read()

    img = Image.open(io.BytesIO(file_bytes)) # Converts byte image to PIL Image Object
    predictions = model.classify(img)
    print(predictions[0:3])
    
    