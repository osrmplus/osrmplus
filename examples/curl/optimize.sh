#!/bin/bash
# VRP: optimize deliveries for 2 vehicles and 5 stops.
# Coordinates are [lat, lon]. Index 0 is the depot.

curl -s -X POST "https://api.osrmplus.com/vrp" \
  -H "x-api-key: $OSRMPLUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [31.5497, 74.3436],
      [31.4700, 74.2650],
      [31.5000, 74.3000],
      [31.5200, 74.2800],
      [31.5100, 74.3200],
      [31.4800, 74.2900]
    ],
    "num_vehicles": 2,
    "depot": 0,
    "demands": [0, 3, 2, 4, 6, 4],
    "vehicle_capacities": [10, 10],
    "time_limit_seconds": 10
  }'
