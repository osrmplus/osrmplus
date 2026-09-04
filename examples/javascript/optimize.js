import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

// Coordinates are [lat, lon]. Index 0 is the depot.
const result = await client.vrp({
  coordinates: [
    [31.5497, 74.3436],   // Depot (Gulberg)
    [31.47, 74.265],      // Stop 1 (Model Town)
    [31.5, 74.3],         // Stop 2 (Liberty)
    [31.52, 74.28],       // Stop 3 (Johar Town)
    [31.51, 74.32],       // Stop 4
    [31.48, 74.29],       // Stop 5
  ],
  num_vehicles: 2,
  depot: 0,
  demands: [0, 3, 2, 4, 6, 4],
  vehicle_capacities: [10, 10],
  time_limit_seconds: 10,
});

console.log(`Status: ${result.status}`);
console.log(`Total distance: ${result.total_distance}`);
console.log(`Vehicles used: ${result.statistics.vehicles_used}`);

for (const r of result.routes) {
  console.log(`  Vehicle ${r.vehicle_id}: [${r.route}] (distance ${r.distance})`);
}

if (result.dropped_nodes.length) {
  console.log(`Dropped stops: ${result.dropped_nodes}`);
}
