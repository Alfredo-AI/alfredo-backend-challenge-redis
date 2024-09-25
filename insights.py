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