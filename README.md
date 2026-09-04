# OSRMPlus

Routing, distance matrices, and fleet optimization in one API.
OSRM-compatible, nothing to install or run yourself.

**Website:** [osrmplus.com](https://osrmplus.com)
| **Docs:** [osrmplus.com/docs](https://osrmplus.com/docs)
| **Playground:** [osrmplus.com/playground](https://osrmplus.com/playground)

---

## Install

```bash
pip install osrmplus
```

```bash
npm install osrmplus
```

## Quick start (Python)

```python
from osrmplus import Client

client = Client("your_api_key")

# Route between two points
route = client.route([(74.3436, 31.5497), (74.2650, 31.4700)])
print(route["routes"][0]["distance"], "meters")
print(route["routes"][0]["duration"], "seconds")

# Distance matrix
matrix = client.matrix(
    coordinates=[(74.34, 31.55), (74.27, 31.47), (74.30, 31.50)]
)
print(matrix["durations"])  # 3x3 array of seconds

# Optimize a delivery round (VRP)
plan = client.optimize(
    vehicles=[{"id": 1, "start": [74.3436, 31.5497], "capacity": [20]}],
    jobs=[
        {"id": 1, "location": [74.2650, 31.4700], "delivery": [5]},
        {"id": 2, "location": [74.3000, 31.5000], "delivery": [8]},
        {"id": 3, "location": [74.2800, 31.5200], "delivery": [3]},
    ],
)
for route in plan["routes"]:
    print(f"Vehicle {route['vehicle']}: {len(route['steps'])} stops")
```

## Quick start (JavaScript / TypeScript)

```typescript
import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

// Route between two points
const route = await client.route([[74.3436, 31.5497], [74.265, 31.47]]);
console.log(route.routes[0].distance, "meters");

// Distance matrix
const matrix = await client.matrix({
  coordinates: [[74.34, 31.55], [74.27, 31.47], [74.3, 31.5]],
});
console.log(matrix.durations); // 3x3 array

// Optimize a delivery round (VRP)
const plan = await client.optimize({
  vehicles: [{ id: 1, start: [74.3436, 31.5497], capacity: [20] }],
  jobs: [
    { id: 1, location: [74.265, 31.47], delivery: [5] },
    { id: 2, location: [74.3, 31.5], delivery: [8] },
    { id: 3, location: [74.28, 31.52], delivery: [3] },
  ],
});
```

## Quick start (curl)

```bash
# Get an API key at https://osrmplus.com (free tier, no credit card)

# Route
curl "https://api.osrmplus.com/route/v1/driving/74.3436,31.5497;74.2650,31.4700" \
  -H "x-api-key: YOUR_KEY"

# Distance matrix
curl "https://api.osrmplus.com/table/v1/driving/74.34,31.55;74.27,31.47;74.30,31.50" \
  -H "x-api-key: YOUR_KEY"

# Snap to nearest road
curl "https://api.osrmplus.com/nearest/v1/driving/74.3436,31.5497" \
  -H "x-api-key: YOUR_KEY"

# VRP (fleet optimization)
curl -X POST "https://api.osrmplus.com/vrp" \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": [{"id": 1, "start": [74.3436, 31.5497], "capacity": [20]}],
    "jobs": [
      {"id": 1, "location": [74.2650, 31.4700], "delivery": [5]},
      {"id": 2, "location": [74.3000, 31.5000], "delivery": [8]}
    ]
  }'
```

---

## API endpoints

All endpoints are at `https://api.osrmplus.com`. Send your key as `x-api-key` or `Authorization: Bearer`.

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/route/v1/driving/{coords}` | Point-to-point route with distance and duration |
| GET | `/table/v1/driving/{coords}` | Distance and duration matrix between all points |
| GET | `/nearest/v1/driving/{coord}` | Snap a coordinate to the nearest road |
| GET | `/match/v1/driving/{coords}` | Match GPS traces to the road network |
| POST | `/vrp` | Multi-vehicle route optimization with constraints |
| POST | `/tsp` | Shortest round trip through a set of stops |
| POST | `/optimize` | VRP with sensible defaults |

Coordinates in GET endpoints are `lng,lat` pairs separated by semicolons.
Coordinates in POST endpoints are `[lng, lat]` arrays.

### Route response

```json
{
  "code": "Ok",
  "routes": [{
    "distance": 12453.2,
    "duration": 847.3,
    "geometry": "encoded_polyline_here",
    "legs": [...]
  }]
}
```

### Matrix response

```json
{
  "code": "Ok",
  "durations": [[0, 234.5, 567.8], [234.5, 0, 345.6], [567.8, 345.6, 0]],
  "distances": [[0, 3200, 7800], [3200, 0, 4500], [7800, 4500, 0]]
}
```

### VRP/Optimize request

```json
{
  "vehicles": [
    {
      "id": 1,
      "start": [74.3436, 31.5497],
      "end": [74.3436, 31.5497],
      "capacity": [20],
      "time_window": [1695000000, 1695028800]
    }
  ],
  "jobs": [
    {
      "id": 1,
      "location": [74.2650, 31.4700],
      "delivery": [5],
      "time_windows": [[1695003600, 1695014400]],
      "service": 300,
      "priority": 2
    }
  ]
}
```

### VRP/Optimize response

```json
{
  "code": "Ok",
  "routes": [
    {
      "vehicle": 1,
      "cost": 2847,
      "steps": [
        {"type": "start", "location": [74.3436, 31.5497], "arrival": 1695000000},
        {"type": "job", "id": 1, "location": [74.2650, 31.4700], "arrival": 1695003900},
        {"type": "end", "location": [74.3436, 31.5497], "arrival": 1695007200}
      ]
    }
  ],
  "unassigned": []
}
```

---

## Pricing

Start free, no credit card needed.

| Plan | Matrix elements | Routing calls | Regions | Price |
|------|----------------|---------------|---------|-------|
| Free | 50K/mo | 1K/mo | 1 | $0 |
| Growth | 500K/mo | 10K/mo | 2 | $79/mo |
| Scale | 5M/mo | 100K/mo | All | $299/mo |
| Enterprise | Unlimited | Unlimited | All | Custom |

A matrix element is one origin-destination pair. A 10x10 matrix is 100 elements.

---

## SDK reference

### Python

```python
from osrmplus import Client

client = Client(api_key, base_url="https://api.osrmplus.com")

# Routing
client.route(coordinates, **params)        # list of (lng, lat) tuples
client.nearest(coordinate, **params)       # single (lng, lat) tuple
client.match(coordinates, **params)
client.trip(coordinates, **params)

# Matrices
client.matrix(coordinates, **params)       # full NxN
client.matrix(coordinates, sources=[0], destinations=[1,2], **params)

# Optimization
client.vrp(vehicles, jobs, **params)
client.tsp(coordinates, **params)
client.optimize(vehicles, jobs, **params)
```

All methods return the parsed JSON response as a dict. Errors raise `osrmplus.APIError` with `.status_code`, `.code`, and `.message`.

### JavaScript / TypeScript

```typescript
import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus(apiKey, { baseUrl: "https://api.osrmplus.com" });

// Routing
await client.route(coordinates, params?)
await client.nearest(coordinate, params?)
await client.match(coordinates, params?)
await client.trip(coordinates, params?)

// Matrices
await client.matrix({ coordinates, sources?, destinations?, annotations? })

// Optimization
await client.vrp({ vehicles, jobs })
await client.tsp({ coordinates })
await client.optimize({ vehicles, jobs })
```

All methods return the parsed JSON response. Errors throw `OSRMPlusError` with `.statusCode`, `.code`, and `.message`.

---

## Links

- [Website](https://osrmplus.com)
- [Documentation](https://osrmplus.com/docs)
- [Playground](https://osrmplus.com/playground)
- [Contact](https://osrmplus.com/contact)

## License

The SDKs in this repository are MIT licensed. The API service is operated by [Logistr LLC](https://logistr.com).
