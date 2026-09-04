# osrmplus

JavaScript/TypeScript client for the [OSRMPlus](https://osrmplus.com) routing, matrix, and fleet optimization API.

No dependencies. Works in Node.js 18+ and modern browsers.

## Install

```bash
npm install osrmplus
```

## Usage

```typescript
import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

// Route (coordinates are [lng, lat])
const route = await client.route([[74.3436, 31.5497], [74.265, 31.47]]);

// Distance matrix (coordinates are [lng, lat])
const matrix = await client.matrix({
  coordinates: [[74.34, 31.55], [74.27, 31.47], [74.3, 31.5]],
});

// Fleet optimization (coordinates are [lat, lon])
const result = await client.vrp({
  coordinates: [[31.5497, 74.3436], [31.47, 74.265], [31.5, 74.3]],
  num_vehicles: 2,
  depot: 0,
  demands: [0, 3, 2],
  vehicle_capacities: [6, 6],
  time_limit_seconds: 10,
});
console.log(result.status); // "ROUTING_SUCCESS"
```

Full docs at [osrmplus.com/docs](https://osrmplus.com/docs).
