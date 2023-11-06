# YOUR API HERE
from re import S
from fastAPI import FastAPI
from pydantic import BaseModel
from redis.commands.search.aggregation import AggregateRequest
from redis.commands.search.query import Query
from redis.exceptions import ResponseError

import json
import redis


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


#connect to redis
client = redis.Redis(decode_responses=True, protocol=3)

#start API application
app = FastAPI()

@app.post("/metrics")
def property_in_type(property_id: int, property: Property):


    addType_search_full = property.addType.split(",")
    assetType_search_full = property.assetType.split(",")
    county_search_full = property.county.split(",")
    numberOfRooms_search_full = property.numberOfRooms.split(",")
    

    addType_search_clause = ""
    assetType_search_clause = ""

    for addType_search in addType_search_full:
        addType_search_clause = f"{addType_search_clause} @:addType {{{addType_search}}}"

    for assetType_search in assetType_search_full:
        assetType_search_clause = f"{assetType_search_clause} @:assetype {{{assetType_search}}}"

    for county_search in county_search_full:
        county_search_clause = f"{county_search_clause} @:county {{{county_search}}}"

    for county_search in county_search_full:
        county_search_clause = f"{county_search_clause} @:county {{{county_search}}}"


    addType_search_result = client.ft("property_index_json").search(
        Query()
    )

def metrics():

    return 


#search by range of values: price, grossArea, enteredMarket; represented by a dictionary [min max]
##
res_price = client.ft("property_index_json").search(
    Query("@price: [min_price max_price]")
)

res_grossArea = client.ft("property_index_json").search(
    Query("@grossArea: [min_area max_area]")
)

res_enteredMarket = client.ft("property_index_json").search(
    Query("@enteredMarket: [min_market max_market]")
)
##


#search by single or multiple values