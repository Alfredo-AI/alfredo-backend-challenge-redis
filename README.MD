# Alfredo Backend Challenge

This challenge consists of building a _Redis_ database and using it to calculate several useful metrics on the real estate market. The user will access these metrics through a _REST_ API endpoint, built on the _FastAPI_ library.

To do that you will have to follow these steps:

1. Create a _Redis_ database, and add an index with the schema mentioned below.
2. Load the JSON file and add the entries inside to the database (you can access the JSON file [here](https://backend-challenge.s3.fr-par.scw.cloud/data.json)
3. Create a basic _FastAPI_ backend, with a single `POST /metrics` endpoint, that calculates the metrics specified below and returns them to the user.

These steps will be explained in further detail in the sections below.

## Main Technologies

- [Redis](https://redis.io/) - Redis is an in-memory key–value database, cache and message broker.
- [redis-py](https://github.com/redis/redis-py) - A Redis client for Python.
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework for building APIs with Python
- [Docker](https://docs.docker.com/get-started/) - A platform for developing, shipping, and running applications in containers, which are lightweight, isolated environments that ensure consistent deployment across different computing environments.

## Setup

This challenge is going to run on top of _Python_ version `3.10.11`, for which we recomend you to use a [virtual environment](https://docs.python.org/3/library/venv.html) in order to compartmentalize any packages you install from your system's native _Python_ installation.

To run a _Redis_ database in your machine we will use the [Docker](https://docs.docker.com/get-started/) technology.

After you install it, run the command:

```sh
docker run -e REDISEARCH_ARGS="TIMEOUT 20000 --save 3600 1500000" -d --name redis-challenge -p 6379:6379 -p 8001:8001 -v redis-stack:/data-redis-challenge redis/redis-stack:latest
```

Which will build a _Redis Stack_ [image](https://hub.docker.com/r/redis/redis-stack) and launch a container. [_Redis Stack_](https://redis.io/docs/about/about-stack/) is a bundle of several `Redis` technologies into a single container, but the ones we are most interested in are:

- [**Search and query**](https://redis.io/docs/interact/search-and-query/): provides querying and data aggregation capabilities. Accessed through `localhost:6379`.
- [**RedisInsight**](https://redis.io/docs/connect/insight/): tool for vizualizing data, and run real time queries and commands. Accessed through `localhost:8001`.

After you have your database set up, we need to install the _Python_ packages needed to run your backend

```bash
pip install fastapi
pip install "uvicorn[standard]"
```

and to access your _Redis_ database through _Python_:

```bash
pip install "redis[hiredis]"
```

## 1. Redis Database Creation

We will use the database to store housing information, where each entry corresponds to a single real estate listing.

Each _Redis_ database entry will have a unique `property_id` key matching to a _Redis_ [index](https://redis.io/docs/interact/search-and-query/indexing/) that follows the given [schema](https://redis.io/docs/interact/search-and-query/basic-constructs/schema-definition/):

```py
{
    "addType": TextField,
    "assetType": TextField,
    "county": TextField,
    "price": NumericField,
    "grossArea": NumericField,
    "numberOfRooms": NumericField,
    "enteredMarket": NumericField
}
```

- `addType`: Type of listing, if it's a **sell** or a **rent** property
- `assetType`: Property type, it can be **house**, **apartment**, **store**, **land**, etc..
- `county`: Which county the property is located in. (In portuguese: 'Concelho').
- `price`: Listed price.
- `grossArea`: The property's gross area.
- `numberOfRooms`: The property's number of rooms.
- `enteredMarket`: Datetime of when the property entered the market, encoded as an integer.

You can follow [this](https://redis-py.readthedocs.io/en/stable/redismodules.html#redisearch-commands) example from the `Redis` `Python` client, on how to create a new index.

Just make sure that whenever you initialize a `Redis` client we select the [latest protocol](https://github.com/redis/redis-py#resp3-support) of data serialization avaliable. Also enable response decoding, so that we don't receive data in binary format.

```py
from redis import Redis

client = Redis(decode_responses=True, protocol=3)
```

## 2. Load JSON file

The dataset is stored in the `data.json` file, located [here](https://backend-challenge.s3.fr-par.scw.cloud/data.json). We want to create Python logic to load it into a variable, process it, and upload it into our _Redis_ database.

Split each of these steps into multiple _Python_ functions and store them in the `utils.py` file.

## 3. FastAPI backend

With our database loaded and ready to go, we want to create a backend to access it and return information to our users.

We will use the [FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/) library to build a REST API. This will be comprised of a single endpoint:

`POST /metrics`

This endpoint will receive a [payload](https://fastapi.tiangolo.com/tutorial/schema-extra-example/) of property filters, which we will use to filter through our databse.

For example:

```json
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
```

As we can observe, we want to be able to query in several different fashions.

- **Categorical** fields (`addType`, `assetType`, `county`, `numberOfRooms`) - can be queried by a single or multiple values. Represented by the value itself or an array of values.
- **Continuous** fields (`price`, `grossArea`, `enteredMarket`) - can be queried by a range of values. Represented by a dictionary (object), with two possible minimum/maximum keys.

After doing so we want to use [_Redis_ aggregate funcions](https://redis.io/docs/interact/search-and-query/search/aggregations/) to calculate the following metrics:

- Average grossArea:
- Median Price
- Total number of rooms.
- Number of rooms bar graph.

**Hint:** Take a look at this [example](https://redis.io/docs/connect/clients/python/#example-indexing-and-querying-json-documents). It uses the _Redis_ _Python_ client to, among other things, perform aggregate functions.

We want the endpoint's [response model](https://fastapi.tiangolo.com/tutorial/response-model/) to follow this format

```json
{
  "avgArea": {
    "data": "<value>",
    "type": "indicator",
    "unit": "m²"
  },
  "medianPrice": {
    "data": "<value>",
    "type": "indicator",
    "unit": "€"
  },
  "totalCount": {
    "data": "<value>",
    "type": "indicator",
    "unit": ""
  },
  "roomCount": {
    "data": [
      {
        "x": "0",
        "<county 1>": "<count county 1>",
        "<county 2>": "<count county 2>",
        "total": "<count sum>"
      },
      {
        "x": "1",
        "<county 1>": "<count county 1>",
        "<county 2>": "<count county 2>",
        "total": "<count sum>"
      },
      {
        "x": "2",
        "<county 1>": "<count county 1>",
        "<county 2>": "<count county 2>",
        "total": "<count sum>"
      },
      {
        "x": "3",
        "<county 1>": "<count county 1>",
        "<county 2>": "<count county 2>",
        "total": "<count sum>"
      }
    ],
    "type": "bar",
    "unit": ""
  }
}
```

## Tips

- Make sure to write clean, well commented code, with discriptive variables.
- Try to keep functions as suscint as possible. Remember: 2 small functions are better than 1 larger one.
- Avoid function nesting as much as you can. Keeping code "depth" to 2/3 functions deep makes debugging easier.
- [Type hints](https://docs.python.org/3/library/typing.html) are not only helpful for code reading but also for code writing. They enhance your IDE's IntelliSense/Autocomplete abilities.
- Commit your code (very) often and with descriptive messages. Multiple very small commits are always better that one giant one. If something goes wrong it's easier to revert.
