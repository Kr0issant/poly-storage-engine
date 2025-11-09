from pydantic import BaseModel
class Item(BaseModel):
    name:str

class Directory(Item):
    content:list

class JSON(Item):
    content:dict

class Img(Item):
    content:bytes
