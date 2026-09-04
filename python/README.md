# osrmplus

Python client for the [OSRMPlus](https://osrmplus.com) routing, matrix, and fleet optimization API.

No dependencies. Works with Python 3.9+.

## Install

```bash
pip install osrmplus
```

## Usage

```python
from osrmplus import Client

client = Client("your_api_key")

# Route (coordinates are (lng, lat) tuples)
route = client.route([(74.3436, 31.5497), (74.2650, 31.4700)])

# Distance matrix (coordinates are (lng, lat) tuples)
matrix = client.matrix(
    coordinates=[(74.34, 31.55), (74.27, 31.47), (74.30, 31.50)]
)

# Fleet optimization (coordinates are [lat, lon])
result = client.vrp(
    coordinates=[[31.5497, 74.3436], [31.4700, 74.2650], [31.5000, 74.3000]],
    num_vehicles=2,
    depot=0,
    demands=[0, 3, 2],
    vehicle_capacities=[6, 6],
    time_limit_seconds=10,
)
print(result["status"])  # "ROUTING_SUCCESS"
```

Full docs at [osrmplus.com/docs](https://osrmplus.com/docs).
