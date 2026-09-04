#!/bin/bash
# Route between two points in Lahore

curl -s "https://api.osrmplus.com/route/v1/driving/74.3436,31.5497;74.2650,31.4700?overview=full&steps=true" \
  -H "x-api-key: $OSRMPLUS_API_KEY"
