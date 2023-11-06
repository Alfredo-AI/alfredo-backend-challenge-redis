# YOUR API HERE
from re import S
from fastAPI import FastAPI
from pydantic import BaseModel
from redis.commands.search.aggregation import AggregateRequest
from redis.commands.search.query import Query
from redis.exceptions import ResponseError

import json
import redis


app = FastAPI()

class Property(BaseModel):
    addType: str
    assetType: str
    county: str
    price: float
    grossArea: float
    numberOfRooms: int
    enteredMarket: float

    model_config = {
        "json_schema": {
            "examples" : [
                {
                    "addType": "sell",
                    "assetType": ["apartment", "house"],
                    "grossArea": {
                        "min": 50,
                        "max": 100
                                },
                    "enteredMarket": {
                    "min": "2023-10-20"
                    }

                }
            ]  
        }
    }


@app.post("/metrics")
def metrics():

    return 