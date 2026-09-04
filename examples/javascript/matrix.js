import { OSRMPlus } from "osrmplus";

const client = new OSRMPlus("your_api_key");

const result = await client.matrix({
  coordinates: [
    [74.3436, 31.5497], // Gulberg
    [74.265, 31.47],    // Model Town
    [74.3, 31.5],       // Liberty
    [74.28, 31.52],     // Johar Town
  ],
  annotations: "duration,distance",
});

console.log("Duration matrix (seconds):");
console.table(result.durations);

console.log("Distance matrix (meters):");
console.table(result.distances);
