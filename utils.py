from math import cos, sin, sqrt, asin


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return the distance in km between two points around the Earth.

    Latitude and longitude for each point are given in degrees.
    """
    if not (type(lat1) == int or type(lat1) == float):
        raise TypeError("Latitude 1 is not of accepted numeric type")

    if not (-90 <= lat1 <= 90):
        raise ValueError("Invalid latitude 1 given (should be in range -90 to 90)")

    if not (type(lon1) == int or type(lon1) == float):
        raise TypeError("Longitude 1 is not of accepted numeric type")

    if not (-180 <= lon1 <= 180):
        raise ValueError("Invalid longitude 1 given (should be in range -180 to 180)")

    if not (type(lat2) == int or type(lat2) == float):
        raise TypeError("Latitude 2 is not of accepted numeric type")

    if not (-90 <= lat2 <= 90):
        raise ValueError("Invalid latitude 2 given (should be in range -90 to 90)")

    if not (type(lon2) == int or type(lon2) == float):
        raise TypeError("Longitude 2 is not of accepted numeric type")

    if not (-180 <= lon2 <= 180):
        raise ValueError("Invalid longitude 2 given (should be in range -180 to 180)")

    R = 6371
    inner = pow(sin((lat2 - lat1) / 2), 2) + cos(lat1) * cos(lat2) * pow(sin((lon2 - lon1) / 2), 2)
    d = 2 * R * asin(sqrt(inner))

    return d
