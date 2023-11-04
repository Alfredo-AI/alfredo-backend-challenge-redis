# YOUR FUNCTIONS HERE

import redis
from redis.commands.search.field import TextField
from redis.commands.search.field import NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.json.path import Path
import json
from types import SimpleNamespace




def create_index():
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
    pipeline.json().set(property_key, '$', property)
    property_key = 'PROPERTY_KEY_'

  pipeline.execute()
  
 



client = redis.Redis(decode_responses=True, protocol=3)

#create_index()
property_data = load_property_data()
redis_set_property_data(client,property_data)




