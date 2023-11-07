# YOUR API HERE
from ast import List
from functools import reduce
from re import S
from fastapi import FastAPI
from pydantic import BaseModel
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.aggregation import AggregateRequest
from redis.commands.search.query import Query
from redis.exceptions import ResponseError
#from utils import unix_date_time_search
import json
import redis
from datetime import datetime


class Property(BaseModel):
   
    addType: str 
    assetType: str | list[str]
    county: str #| list[str]
    price: dict
    grossArea: dict
    enteredMarket: dict
    #numberOfRooms: str


#connect to redis
client = redis.Redis(decode_responses=True, protocol=3)

#start API application
app = FastAPI()

#@app.post("/metrics")
@app.post("/metrics")
def property_in_type(property: Property):

    #s_clause = make_search_clause()
    rs = client.ft("property_index_json")
    

    #clause constructor
    assetType_clause = string_or_list(property.assetType)
    county_clause = string_or_list(property.county)
    p_min = property.price["min"]
    p_max = property.price["max"]
    gA_min = property.grossArea["min"]
    gA_max = property.grossArea["max"]
    date_min = unix_date_time_search(property.enteredMarket["min"])
    date_max = unix_date_time_search(property.enteredMarket["max"])

    search_clause=(f" @addType: {property.addType} @assetType: {assetType_clause} @county:{county_clause} @price:[{p_min} {p_max}] @grossArea:[{gA_min} {gA_max}] @enteredMarket:[{date_min} {date_max}]")

    
    
    '''
    ####-----QUERY: in case we just want to query-----###

    query_result = client.ft("property_index_json").search(
        Query(search_clause))
    '''
    
    '''---#==METRICS==#---'''
    #avgGrossArea  ----  
    request_avgArea = AggregateRequest(search_clause).group_by([], reducers.avg('@grossArea').alias("Average Gross Area"))
    result_avgArea = rs.aggregate(request_avgArea)
    #isto e um dict
    d_avgArea = result_avgArea["results"][0]
    #o resultado e:
    avg_area_metric = d_avgArea["extra_attributes"]


    #median price  ----
    request_medPrice = AggregateRequest(search_clause).group_by([], reducers.quantile('@price', '0.5').alias("Median price"))
    result_medPrice = rs.aggregate(request_medPrice)
    #isto e um dict
    d_medPrice = result_medPrice["results"][0]
    #o resultado e:
    medPrice_metric = d_medPrice["extra_attributes"]

    ###total count ----
    query_result = client.ft("property_index_json").search(Query(search_clause))
    total_count = query_result["total_results"]

    return total_count



    #request = AggregateRequest(clause).group_by(['@price'], reducers.count().alias(""))
def string_or_list(input):
    if isinstance(input, str):
        return input
    elif isinstance(input, list):
        return '|'.join(f"{item}" for item in input)
    else:
        return 'Null'
    
def unix_date_time_search(propertydatefield):
    datetime_property = datetime.strptime(propertydatefield, '%Y-%m-%d')
    return datetime_property.timestamp()
       

#return
#return {
#           "avgArea": {
#           "data": "<value>",
#           "type": "indicator",
#           "unit": "m2"
# },
#
#
# }


#number of rooms andd county
#request = AggregateRequest(search_clause).group_by(['@numberOfRooms','@county'], reducers.count().alias("rooms"))


#request = AggregateRequest(clause).group_by([], reducers.max('@price').alias("max price"))



#group by room
#request = AggregateRequest('*').group_by([], reducers.count("@price").alias("max price"))

#average grossArea
#


#procura e total count

    #result = rs.search(
    #    Query("house")
    #)


    # total_count
    #total_count = result["total_results"]



#aggregate max price
#rs = client.ft("property_index_json")
   
    
    #request = AggregateRequest('*').group_by([], reducers.max("@price").alias("max price"))

    #result = rs.aggregate(request)
    

    #return result



