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

# Route between two points (coordinates are lng,lat)
route = client.route([(74.3436, 31.5497), (74.2650, 31.4700)])
print(route["routes"][0]["distance"], "meters")
print(route["routes"][0]["duration"], "seconds")

# Distance matrix (coordinates are lng,lat)
matrix = client.matrix(
    coordinates=[(74.34, 31.55), (74.27, 31.47), (74.30, 31.50)]
)
print(matrix["durations"])  # 3x3 array of seconds

# Optimize a delivery round (coordinates are [lat, lon])
plan = client.optimize(
    coordinates=[[31.5497, 74.3436], [31.4700, 74.2650], [31.5000, 74.3000], [31.5200, 74.2800]],
)
for r in plan["routes"]:
    print(f"Vehicle {r['vehicle_id']}: route {r['route']}, distance {r['distance']}")

# VRP with constraints (coordinates are [lat, lon])
result = client.vrp(
    coordinates=[[31.5497, 74.3436], [31.4700, 74.2650], [31.5000, 74.3000], [31.5200, 74.2800]],
    num_vehicles=2,
    depot=0,
    demands=[0, 3, 2, 4],
    vehicle_capacities=[6, 6],
    time_limit_seconds=10,
)
print(result["status"])           # "ROUTING_SUCCESS"
print(result["total_distance"])
```

## Quick start (JavaScript / TypeScript)

```typescript
import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

// Route between two points (coordinates are lng,lat)
const route = await client.route([[74.3436, 31.5497], [74.265, 31.47]]);
console.log(route.routes[0].distance, "meters");

// Distance matrix (coordinates are lng,lat)
const matrix = await client.matrix({
  coordinates: [[74.34, 31.55], [74.27, 31.47], [74.3, 31.5]],
});
console.log(matrix.durations); // 3x3 array

// Optimize a delivery round (coordinates are [lat, lon])
const plan = await client.optimize({
  coordinates: [[31.5497, 74.3436], [31.47, 74.265], [31.5, 74.3], [31.52, 74.28]],
});

// VRP with constraints (coordinates are [lat, lon])
const result = await client.vrp({
  coordinates: [[31.5497, 74.3436], [31.47, 74.265], [31.5, 74.3], [31.52, 74.28]],
  num_vehicles: 2,
  depot: 0,
  demands: [0, 3, 2, 4],
  vehicle_capacities: [6, 6],
  time_limit_seconds: 10,
});
```

## Quick start (curl)

```bash
# Get an API key at https://osrmplus.com (free tier, no credit card)

# Route (coordinates are lng,lat separated by semicolons)
curl "https://api.osrmplus.com/route/v1/driving/74.3436,31.5497;74.2650,31.4700" \
  -H "x-api-key: YOUR_KEY"

# Distance matrix (coordinates are lng,lat)
curl "https://api.osrmplus.com/table/v1/driving/74.34,31.55;74.27,31.47;74.30,31.50" \
  -H "x-api-key: YOUR_KEY"

# Snap to nearest road
curl "https://api.osrmplus.com/nearest/v1/driving/74.3436,31.5497" \
  -H "x-api-key: YOUR_KEY"

# VRP (coordinates are [lat, lon] in the JSON body)
curl -X POST "https://api.osrmplus.com/vrp" \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [[31.5497,74.3436],[31.4700,74.2650],[31.5000,74.3000],[31.5200,74.2800]],
    "num_vehicles": 2,
    "depot": 0,
    "demands": [0, 3, 2, 4],
    "vehicle_capacities": [6, 6],
    "time_limit_seconds": 10
  }'

# Optimize (picks fleet size and search parameters automatically)
curl -X POST "https://api.osrmplus.com/optimize" \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [[31.5497,74.3436],[31.4700,74.2650],[31.5000,74.3000],[31.5200,74.2800]]
  }'
```

---

## Coordinate conventions

OSRM endpoints (`/route`, `/table`, `/nearest`, `/match`, `/trip`) use **lng,lat** in the URL path, separated by semicolons. This is the standard OSRM convention.

Optimization endpoints (`/vrp`, `/tsp`, `/optimize`) take a JSON body where coordinates are **[lat, lon]** arrays. Index 0 is the depot unless you specify otherwise.

---

## API endpoints

All endpoints are at `https://api.osrmplus.com`. Send your key as `x-api-key` or `Authorization: Bearer`.

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/route/v1/driving/{coords}` | Point-to-point route with distance and duration |
| GET | `/table/v1/driving/{coords}` | Distance and duration matrix between all points |
| GET | `/nearest/v1/driving/{coord}` | Snap a coordinate to the nearest road |
| GET | `/match/v1/driving/{coords}` | Match GPS traces to the road network |
| GET | `/trip/v1/driving/{coords}` | Fastest round trip through all points |
| POST | `/vrp` | Multi-vehicle route optimization with constraints |
| POST | `/tsp` | Shortest tour through all stops (single vehicle) |
| POST | `/optimize` | VRP with sensible defaults |

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

### VRP request

Coordinates are `[lat, lon]`. Every per-node array (demands, time_windows, service_times) follows the same order as the coordinates.

```json
{
  "coordinates": [[24.71, 46.67], [24.72, 46.68], [24.73, 46.69], [24.70, 46.66]],
  "num_vehicles": 2,
  "depot": 0,
  "demands": [0, 3, 2, 4],
  "vehicle_capacities": [6, 6],
  "time_limit_seconds": 10
}
```

**Key VRP fields:**

| Field | Type | Description |
|-------|------|-------------|
| `coordinates` | `[[lat, lon], ...]` | Stop locations. A road distance matrix is built internally. |
| `distance_matrix` | `[[int, ...], ...]` | Precomputed matrix, used instead of coordinates. |
| `num_vehicles` | int | Fleet size. |
| `depot` | int | Shared start/end node for all vehicles (default 0). |
| `demands` | `[int]` | Load demand at each stop. Requires `vehicle_capacities`. |
| `vehicle_capacities` | `[int]` | Maximum capacity for each vehicle. |
| `time_windows` | `[[start, end]]` | Earliest and latest arrival time at each stop. |
| `service_times` | `[int]` | Time spent at each stop before departing. |
| `time_limit_seconds` | int | How long the solver may search (default 30). |
| `allow_dropping_visits` | bool | Let the solver skip stops when the problem is infeasible. |
| `drop_penalty` | int | Cost of skipping a stop. |
| `detailed_solution` | bool | Include coordinates and arrival times in the response. |
| `objective` | string | `minimize_total_distance` (default), `minimize_longest_route`, `minimize_total_time`, or `minimize_vehicles_used`. |

### VRP/Optimize response

```json
{
  "job_id": "abc123",
  "status": "ROUTING_SUCCESS",
  "routes": [
    { "vehicle_id": 0, "route": [0, 2, 1, 0], "distance": 4210, "load": 5 }
  ],
  "total_distance": 8300,
  "max_route_distance": 4210,
  "dropped_nodes": [],
  "statistics": { "vehicles_used": 2, "num_locations": 4, "solve_time_ms": 1820 }
}
```

Always check `status`. An infeasible problem returns `200` with `"status": "NO_SOLUTION_FOUND"`.

---

## SDK reference

### Python

```python
from osrmplus import Client

client = Client(api_key, base_url="https://api.osrmplus.com")

# Routing (coordinates are (lng, lat) tuples)
client.route(coordinates, **params)
client.nearest(coordinate, **params)
client.match(coordinates, **params)
client.trip(coordinates, **params)

# Matrix (coordinates are (lng, lat) tuples)
client.matrix(coordinates, sources=[0], destinations=[1,2], **params)

# Optimization (coordinates are [lat, lon] lists)
client.vrp(coordinates=..., num_vehicles=..., **params)
client.tsp(coordinates=..., **params)
client.optimize(coordinates=..., **params)
```

All methods return the parsed JSON response as a dict. Errors raise `osrmplus.APIError` with `.status_code`, `.code`, and `.message`.

### JavaScript / TypeScript

```typescript
import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus(apiKey, { baseUrl: "https://api.osrmplus.com" });

// Routing (coordinates are [lng, lat])
await client.route(coordinates, params?)
await client.nearest(coordinate, params?)
await client.match(coordinates, params?)
await client.trip(coordinates, params?)

// Matrix (coordinates are [lng, lat])
await client.matrix({ coordinates, sources?, destinations?, annotations? })

// Optimization (coordinates are [lat, lon])
await client.vrp({ coordinates, num_vehicles, depot?, demands?, vehicle_capacities?, ... })
await client.tsp({ coordinates, ... })
await client.optimize({ coordinates, ... })
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
