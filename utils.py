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

  with open('/home/leon/Desktop/data2.json', 'r') as file:
    p_data = json.load(file)

  return p_data


def redis_set_property_data(d):
  property_UID =0
  

  for property in d:
    property_UID =+1
    pipeline.json().set(property_UID, '$', property)
  
  


### start
client = redis.Redis(decode_responses=True, protocol=3)

#create_index()
pipeline = client.pipeline(transaction = False)
property_data = load_property_data()
redis_set_property_data(property_data)
pipeline.execute()



'''
property_UID = 0
for property in property_data:
  property_UID += 1
  pipeline.json().set(property_UID, "$", property)

pipeline.execute()
'''
