#!/bin/bash
# Distance matrix between 4 points

curl -s "https://api.osrmplus.com/table/v1/driving/74.3436,31.5497;74.2650,31.4700;74.3000,31.5000;74.2800,31.5200?annotations=duration,distance" \
  -H "x-api-key: $OSRMPLUS_API_KEY"
