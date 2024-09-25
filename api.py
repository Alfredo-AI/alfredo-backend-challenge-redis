# YOUR API HERE
from ast import List
from functools import reduce
from re import S, search
from fastapi import FastAPI
from pydantic import BaseModel
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.aggregation import AggregateRequest, Asc
from redis.commands.search.query import Query
from redis.exceptions import ResponseError

from insights import calculate_median_price, calculate_average_area, calculate_total_count, calculate_rooms_and_county
#from utils import unix_date_time_search

import json
import redis
from datetime import datetime

# Create payload class
class Property(BaseModel):
   
    addType: str 
    assetType: str | list[str]
    county: str | list[str]
    price: dict
    grossArea: dict
    numberOfRooms: str | list[str]
    enteredMarket: dict

# Connect to Redis and Start API application
client = redis.Redis(decode_responses=True, protocol=3)
app = FastAPI()

#create API path operation decorator
@app.post("/metrics")
def property_in_type(property: Property):

    # load redis schema
    rs = client.ft("property_index_json")
    
    # redis clause constructor
    assetType_clause = string_or_list(property.assetType)
    county_clause = string_or_list(property.county)
    numberOfRooms_clause = string_or_list(property.numberOfRooms)
    p_min = property.price["min"]
    p_max = property.price["max"]
    gA_min = property.grossArea["min"]
    gA_max = property.grossArea["max"]
    date_min = unix_date_time_search(property.enteredMarket["min"])
    date_max = unix_date_time_search(property.enteredMarket["max"])

    #@numberOfRooms: {numberOfRooms_clause}
    search_clause=(f" @addType: {property.addType} @assetType: {assetType_clause} @county:{county_clause} @price:[{p_min} {p_max}] @grossArea:[{gA_min} {gA_max}]  @enteredMarket:[{date_min} {date_max}]")

    

    # metrics calculation
    median_price = calculate_median_price(rs, search_clause)
    average_area = calculate_average_area(rs, search_clause)
    total_count = calculate_total_count(rs, search_clause)
    rooms_county = calculate_rooms_and_county(rs, search_clause)
  
    metrics = print_metrics(average_area["Average Gross Area"], median_price["Median price"], total_count)
    
    return metrics, rooms_county

# convert to string if its a list of strings
def string_or_list(input):
    if isinstance(input, str):
        return input
    elif isinstance(input, list):
        return '|'.join(f"{item}" for item in input)
    else:
        return 'Null'
    
# convert search date into unix to query
def unix_date_time_search(propertydatefield):
    datetime_property = datetime.strptime(propertydatefield, '%Y-%m-%d')
    return datetime_property.timestamp()
       
# populate dictionary with metrics attained from query/aggregate
def print_metrics(area,price,roomcount):
    results = {
                "avgArea": {
                    "data": area,
                    "type": "indicator",
                    "unit": "m²"
                },
                "medianPrice": {
                    "data": price,
                    "type": "indicator",
                    "unit": "€"
                },
                "totalCount": {
                    "data": roomcount,
                    "type": "indicator",
                    "unit": ""
                }
        }
    return results

