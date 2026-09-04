import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

const plan = await client.optimize({
  vehicles: [
    { id: 1, start: [74.3436, 31.5497], end: [74.3436, 31.5497], capacity: [20] },
    { id: 2, start: [74.3436, 31.5497], end: [74.3436, 31.5497], capacity: [20] },
  ],
  jobs: [
    { id: 1, location: [74.265, 31.47], delivery: [5], service: 300 },
    { id: 2, location: [74.3, 31.5], delivery: [8], service: 300 },
    { id: 3, location: [74.28, 31.52], delivery: [3], service: 300 },
    { id: 4, location: [74.32, 31.51], delivery: [6], service: 300 },
    { id: 5, location: [74.29, 31.48], delivery: [4], service: 300 },
  ],
});

for (const route of plan.routes) {
  const stops = route.steps.filter((s) => s.type === "job");
  console.log(`Vehicle ${route.vehicle}: ${stops.length} deliveries, cost ${route.cost}`);
  for (const s of stops) {
    console.log(`  -> Job ${s.id} at ${s.location}`);
  }
}

if (plan.unassigned.length) {
  console.log(`\n${plan.unassigned.length} jobs could not be assigned`);
}
