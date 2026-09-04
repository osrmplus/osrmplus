"""Plan routes for a fleet of delivery vehicles."""

from osrmplus import Client

client = Client("your_api_key")

plan = client.optimize(
    vehicles=[
        {
            "id": 1,
            "start": [74.3436, 31.5497],
            "end": [74.3436, 31.5497],
            "capacity": [20],
        },
        {
            "id": 2,
            "start": [74.3436, 31.5497],
            "end": [74.3436, 31.5497],
            "capacity": [20],
        },
    ],
    jobs=[
        {"id": 1, "location": [74.2650, 31.4700], "delivery": [5], "service": 300},
        {"id": 2, "location": [74.3000, 31.5000], "delivery": [8], "service": 300},
        {"id": 3, "location": [74.2800, 31.5200], "delivery": [3], "service": 300},
        {"id": 4, "location": [74.3200, 31.5100], "delivery": [6], "service": 300},
        {"id": 5, "location": [74.2900, 31.4800], "delivery": [4], "service": 300},
    ],
)

for r in plan["routes"]:
    stops = [s for s in r["steps"] if s["type"] == "job"]
    print(f"Vehicle {r['vehicle']}: {len(stops)} deliveries, cost {r['cost']}")
    for s in stops:
        print(f"  -> Job {s['id']} at {s['location']}")

if plan["unassigned"]:
    print(f"\n{len(plan['unassigned'])} jobs could not be assigned")
