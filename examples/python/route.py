"""Get a route between two points."""

from osrmplus import Client

client = Client("your_api_key")

route = client.route([
    (74.3436, 31.5497),  # Lahore, start
    (74.2650, 31.4700),  # Lahore, end
])

leg = route["routes"][0]
print(f"Distance: {leg['distance']:.0f} meters")
print(f"Duration: {leg['duration']:.0f} seconds")
