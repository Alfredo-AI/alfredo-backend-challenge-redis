# YOUR FUNCTIONS HERE

from redis import redis
from redis.commands.search.field import TextField
from redis.commands.search.field import NumericField


client = redis.Redis(decode_responses=True, protocol=3)


# = redis.Redis()
index_name = "my_index"
schema = (
    TextField("addType", weight=5.0),
    TextField("assetType"),
    TextField("county"),
    NumericField("price"),
    NumericField("grossArea"),
    NumericField("numberOfRooms"),
    NumericField("enteredMarket"),
)
client.ft(index_name).create_index(schema)
print(r.ft(index_name).info())
