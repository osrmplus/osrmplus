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

# Route
route = client.route([(74.3436, 31.5497), (74.2650, 31.4700)])

# Distance matrix
matrix = client.matrix(
    coordinates=[(74.34, 31.55), (74.27, 31.47), (74.30, 31.50)]
)

# Fleet optimization (VRP)
plan = client.optimize(
    vehicles=[{"id": 1, "start": [74.3436, 31.5497], "capacity": [20]}],
    jobs=[
        {"id": 1, "location": [74.2650, 31.4700], "delivery": [5]},
        {"id": 2, "location": [74.3000, 31.5000], "delivery": [8]},
    ],
)
```

Full docs at [osrmplus.com/docs](https://osrmplus.com/docs).
