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
#from utils import unix_date_time_search

import json
import redis
from datetime import datetime

'''---#==CREATE PAYLOAD==#---'''
class Property(BaseModel):
   
    addType: str 
    assetType: str | list[str]
    county: str | list[str]
    price: dict
    grossArea: dict
    #numberOfRooms: str | list[str]
    enteredMarket: dict


'''---#==CONNECT TO REDIS==#---'''
client = redis.Redis(decode_responses=True, protocol=3)


#start API application
app = FastAPI()

#create API path operation decorator
@app.post("/metrics")
def property_in_type(property: Property):

    #load index to search by
    rs = client.ft("property_index_json")
    

    '''---#==CLAUSE CONSTRUCTOR==#---'''
    assetType_clause = string_or_list(property.assetType)
    county_clause = string_or_list(property.county)
    #numberOfRooms_clause = string_or_list(property.numberOfRooms)
    p_min = property.price["min"]
    p_max = property.price["max"]
    gA_min = property.grossArea["min"]
    gA_max = property.grossArea["max"]
    date_min = unix_date_time_search(property.enteredMarket["min"])
    date_max = unix_date_time_search(property.enteredMarket["max"])

    #@numberOfRooms: {numberOfRooms_clause}
    search_clause=(f" @addType: {property.addType} @assetType: {assetType_clause} @county:{county_clause} @price:[{p_min} {p_max}] @grossArea:[{gA_min} {gA_max}]  @enteredMarket:[{date_min} {date_max}]")

    
    '''####---#==QUERY==#---###
    query_result = client.ft("property_index_json").search(
        Query(search_clause))
    '''
    

    '''---#==METRICS==#---'''
    #Average GrossArea metric ----  
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

#Median Price metric ----  
def calculate_median_price(client, clause):
    request = AggregateRequest(clause).group_by([], reducers.quantile('@price', '0.5').alias("Median price"))
    result = client.aggregate(request)

    #extract result from nested dictionary
    d_result = result["results"][0]
    median_price = d_result["extra_attributes"]

    return median_price

#Average GrossArea metric calculator ----  
def calculate_average_area(client, clause):
    request = AggregateRequest(clause).group_by([], reducers.avg('@grossArea').alias("Average Gross Area"))
    result = client.aggregate(request)

    #extract result from nested dictionary
    d_result = result["results"][0]
    average_area = d_result["extra_attributes"]
    
    return average_area

#Total room count metric ----  
def calculate_total_count(client, clause):
    query_result = client.search(Query(clause))

    #extract result from nested dictionary
    total_count= query_result["total_results"]

    #- This can also be done by aggregate like this:
    #request_totalCount = AggregateRequest(search_clause).group_by([], reducers.count().alias("Total Count"))

    return total_count

#Rooms and County metric ----  
def calculate_rooms_and_county(client, clause):
    request = AggregateRequest(clause).group_by(['@county', '@numberOfRooms',], reducers.count().alias("Total")).sort_by(Asc('@numberOfRooms'))
    room_county_count = client.aggregate(request)

    return room_county_count