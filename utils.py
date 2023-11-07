# YOUR FUNCTIONS HERE

import redis
from redis.commands.search.field import TextField
from redis.commands.search.field import NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.json.path import Path
import json
from types import SimpleNamespace
from datetime import datetime


def create_index():
  client = redis.Redis(decode_responses=True, protocol=3)
  client.ft("property_index_json").create_index(
  [
      TextField("$.addType", as_name = "addType"),
      TextField("$.assetType", as_name ="assetType"),
      #TextField("country")
      TextField("$.county", as_name ="county"),
      #TextField("district"),
      NumericField("$.price", as_name ="price"),
      NumericField("$.grossArea", as_name ="grossArea"),
      NumericField("$.numberOfRooms", as_name ="numberOfRooms"),
      NumericField("$.enteredMarket", as_name ="enteredMarket")
  ],
  definition = IndexDefinition(
    index_type = IndexType.JSON
  )  
)
  return client


def load_property_data():

  with open('/home/leon/Desktop/data.json', 'r') as file:
    p_data = json.load(file)
      
  return p_data


def redis_set_property_data(c,d):
  property_UID = 0
  property_key = 'PROPERTY_KEY_'
  pipeline = c.pipeline(transaction = False)

  for property in d:
    property_UID += 1
    property_key = f"{property_key}{property_UID}"
    enteredMarketUnix = unix_date_time(property)

    new_property = dict(
      addType= property["addType"], 
      assetType= property["assetType"], 
      county= property["county"], 
      price= property["price"], 
      grossArea=property["grossArea"], 
      numberOfRooms= property["numberOfRooms"], 
      enteredMarket= enteredMarketUnix
    )  

    pipeline.json().set(property_key, '$', new_property)
    property_key = 'PROPERTY_KEY_'

  pipeline.execute()
  

def unix_date_time(propertydatefield):
  datetime_str = propertydatefield['enteredMarket'].split("+",1)
  try:
    datetime_property = datetime.strptime(datetime_str[0], '%Y-%m-%d %H:%M:%S.%f')
    return datetime_property.timestamp()
  
  except ValueError:
      datetime_property = datetime.strptime(datetime_str[0], '%Y-%m-%d %H:%M:%S')
      return datetime_property.timestamp()
    

client = create_index()
property_data = load_property_data()
redis_set_property_data(client,property_data)




