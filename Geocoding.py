# -----------------------------------------------------
# Geocoding module by Ricardo Santos.
# Extracts geographic information from an address.
# API used: Google Maps Geocoding API.
# -----------------------------------------------------

# Dependencies
import requests             # Installation: pip3 install requests==2.18.4
from pprint import pprint


geocode_base_url = "https://maps.googleapis.com/maps/api/geocode/json"


def get_GPS_coordinates(address, verbose=False):
    """ Returns approximate coordinates (lat, long) for a given address (can be a postal code). 
        Uses Google Maps Geocoding API: https://developers.google.com/maps/documentation/geocoding/intro?csw=1
    """

    params ={
        # Query parameter
        'address': address,
        'key': 'Replace by your API key',
    }

    response = requests.get(geocode_base_url, headers={}, params=params)
    results = response.json()
    
    ret = [0.0, 0.0]

    try:         
        if len(results["results"]) > 0:
            location = results["results"][0]["geometry"]["location"]
            ret = [location["lat"], location["lng"]]
    except Exception as e:
        print("Error in get_GPS_coordinates: {}".format(e))

    if verbose:
        print("Google Maps Geocoding API return for input '{}':".format(address))
        pprint(results)        
        print("get_GPS_coordinates returning '{}'".format(ret))

    return ret
