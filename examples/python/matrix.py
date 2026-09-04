"""Compute a distance matrix between multiple locations."""

from osrmplus import Client

client = Client("your_api_key")

locations = [
    (74.3436, 31.5497),  # Gulberg
    (74.2650, 31.4700),  # Model Town
    (74.3000, 31.5000),  # Liberty
    (74.2800, 31.5200),  # Johar Town
]

result = client.matrix(
    coordinates=locations,
    annotations="duration,distance",
)

print("Duration matrix (seconds):")
for row in result["durations"]:
    print([f"{v:.0f}" if v else "---" for v in row])

print("\nDistance matrix (meters):")
for row in result["distances"]:
    print([f"{v:.0f}" if v else "---" for v in row])
