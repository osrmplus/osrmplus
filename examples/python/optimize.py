"""Plan routes for a fleet of delivery vehicles."""

from osrmplus import Client

client = Client("your_api_key")

# Coordinates are [lat, lon]. Index 0 is the depot.
result = client.vrp(
    coordinates=[
        [31.5497, 74.3436],   # Depot (Gulberg)
        [31.4700, 74.2650],   # Stop 1 (Model Town)
        [31.5000, 74.3000],   # Stop 2 (Liberty)
        [31.5200, 74.2800],   # Stop 3 (Johar Town)
        [31.5100, 74.3200],   # Stop 4
        [31.4800, 74.2900],   # Stop 5
    ],
    num_vehicles=2,
    depot=0,
    demands=[0, 3, 2, 4, 6, 4],
    vehicle_capacities=[10, 10],
    time_limit_seconds=10,
)

print(f"Status: {result['status']}")
print(f"Total distance: {result['total_distance']}")
print(f"Vehicles used: {result['statistics']['vehicles_used']}")

for r in result["routes"]:
    print(f"  Vehicle {r['vehicle_id']}: {r['route']} (distance {r['distance']}, load {r.get('load', '?')})")

if result["dropped_nodes"]:
    print(f"Dropped stops: {result['dropped_nodes']}")
