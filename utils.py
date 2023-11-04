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

'''
property_UID = 0
for i in range(len(data)):
    data_string = json.dumps(data[i])
    client.set(property_UID, data_string)

    property = json.loads(data_string, object_hook= dict_as)
    #print(property.assetType)
    property_UID = property_UID + 1
'''







#print(data[0])
'''
class Property(object):
  def __init__(self, addType, assetType, country, county, district, enteredMarket, grossArea, numberOfRooms, price):
    self.addType = addType
    self.assetType = assetType
    self.country = country
    self.county = county
    self.district = district
    self.enteredMarket = enteredMarket
    self.grossArea = grossArea
    self.numbmerOfRooms = numberOfRooms
    self.price = price
    
#dct.get('action', None) allow fields to be optional
def dict_as(dct):
  return Property(dct['addType'], dct['assetType'], dct['country'], dct['county'], dct['district'], dct['enteredMarket'], dct['grossArea'], dct['numberOfRooms'], dct['price'])

#data_string = json.dumps(data[1])
#property = json.loads(data_string, object_hook= dict_as)
#print(property.country)
'''






#rs = client.ft()
#rs.create_Index(schema,definition=IndexDefinition(index_type=IndexType.JSON))
#client.json().set( Path.root_path(), data)






#self.__dict__ = json.loads(d)

#p = Property(json.dumps(data[1]))
#print(p.addType)

#deserialized string
#x = json.dumps(data[1])


#x = json.loads(data[1], object_hook=)
#x = json.dumps(data[1])
#print(x)
#Property1 = Property(data)
#print(Property1)
  
'''
class Property(object):
  
p = Property()
with open('/home/leon/Desktop/data2.json', 'r') as file:
    data = json.load(file)

#data = json.load(f)
property_UID = 0


def set_scheme():
    r = redis.Redis()
    index_name = "properties"
    schema = (
      TextField("addType"),
      TextField("assetType"),
      TextField("county"),
      NumericField("price"),
      NumericField("grossArea"),
      NumericField("numberOfRooms"),
      NumericField("enteredMarket")
    )
    r.ft(index_name).create_index(schema)
    print(r.ft(index_name).info())

#define and create schema
index_name = "my_index"

client.ft(index_name).create_index(schema)

for i in data:
    #print(data)
    property_UID = property_UID + 1
    
    #print(client.ft(index_name).info())
    #formatted_data = json.dumps(data, indent=2)
    #print(formatted_data)

    #print(i)count 
    #property_
    #client.set('key_'+str(count),i)

    #print(('key_'+str(count),i))
#f.close()


#for x in

#count 
# Store a key
#print ("set key1 123")
#print (client.set('key1', '123'))

# Retrieve the keycount 
#def create_index(file)

#navegar file

#JSON.SET redis.store



#def getIndex()
#    json =

#JSON.GET store '$..]'


#FT.CREATE {index_name} ON JSON SCHEMA {json_path} AS {attribute} {type}



# = redis.Redis()

#client.ft(index_name).create_index(schema)
#print(client.ft(index_name).info())
'''