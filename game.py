from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from back_unchud import *

app = FastAPI()

class gameData(BaseModel):
    c: str
    price: float
    quantity: int
    name: str
    user: str
    item: str
    bank: float


class gameStuff:
    def __init__(self, user, bank = None):
        self.headS = {"c": "S", "name": "headwear", "price": 120.00, "quantity": 1}
        self.headR = {"c": "R", "name": "headwear", "price": 60.00, "quantity": 1}
        self.headN = {"c": "N", "name": "headwear", "price": 30.00, "quantity": 1}
        self.faceS = {"c": "S", "name": "facewear", "price": 90.00, "quantity": 1}
        self.faceR = {"c": "R", "name": "facewear", "price": 60.00, "quantity": 1}
        self.faceN = {"c": "N", "name": "facewear", "price": 30.00, "quantity": 1}
        self.bodyS = {"c": "S", "name": "body", "price": 150.00, "quantity": 1}
        self.bodyR = {"c": "R", "name": "body", "price": 130.00, "quantity": 1}
        self.bodyN = {"c": "N", "name": "body", "price": 100.00, "quantity": 1}
        self.bottomS = {"c": "S", "name": "headwear", "price": 140.00, "quantity": 1}
        self.bottomR = {"c": "R", "name": "headwear", "price": 130.00, "quantity": 1}
        self.bottomN = {"c": "N", "name": "headwear", "price": 90.00, "quantity": 1}
        self.footS = {"c": "S", "name": "footwear", "price": 100.00, "quantity": 1}
        self.footR = {"c": "R", "name": "footwear", "price": 50.00, "quantity": 1}
        self.footN = {"c": "N", "name": "footwear", "price": 25.00, "quantity": 1}





