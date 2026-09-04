import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

const result = await client.route([
  [74.3436, 31.5497], // Lahore, start
  [74.265, 31.47],    // Lahore, end
]);

const leg = result.routes[0];
console.log(`Distance: ${leg.distance.toFixed(0)} meters`);
console.log(`Duration: ${leg.duration.toFixed(0)} seconds`);
