import requests
import json

# Define the OTP server URL
otp_url = "http://localhost:8080/otp/routers/default/plan"

# Define the origin and destination stops
origin_lat = -21.71425604282143
origin_lon = -43.40818129073404
destination_lat = -21.719036688643843
destination_lon = -43.41020128503543

origin_lat = -31.3
origin_lon = -54.15
destination_lat = -31.25
destination_lon = -54.05


# Set parameters for the OTP API
params = {
    "fromPlace": f"{origin_lat},{origin_lon}",
    "toPlace": f"{destination_lat},{destination_lon}",
    "mode": "TRANSIT,WALK,CAR",  # Transit (bus, train) and walking
    "maxWalkDistance": 1500,  # Maximum walking distance in meters
    "arriveBy": False,  # Set to True for arrival time, False for departure time
    "dateTime": "2025-07-31T06:00:00",  # Departure time (optional)
}

# Send the request to OTP API
response = requests.get(otp_url, params=params)

# Check if the response was successful
if response.status_code == 200:
    data = response.json()
    
    # Print the raw response to debug
    print("Response data:", json.dumps(data, indent=2))
    
    # Extract the route information (e.g., first route option)
    itineraries = data.get('plan', {}).get('itineraries', [])
    
    if itineraries:
        route = itineraries[0]
        print("Route details:", route)
    else:
        print("No route found. The itinerary list is empty.")
else:
    print(f"Error: {response.status_code}")
