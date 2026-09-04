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

// Route
const route = await client.route([[74.3436, 31.5497], [74.265, 31.47]]);

// Distance matrix
const matrix = await client.matrix({
  coordinates: [[74.34, 31.55], [74.27, 31.47], [74.3, 31.5]],
});

// Fleet optimization (VRP)
const plan = await client.optimize({
  vehicles: [{ id: 1, start: [74.3436, 31.5497], capacity: [20] }],
  jobs: [
    { id: 1, location: [74.265, 31.47], delivery: [5] },
    { id: 2, location: [74.3, 31.5], delivery: [8] },
  ],
});
```

Full docs at [osrmplus.com/docs](https://osrmplus.com/docs).
