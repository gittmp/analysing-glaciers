from math import cos, sin, sqrt, asin


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return the distance in km between two points around the Earth.

    Latitude and longitude for each point are given in degrees.
    """
    assert (type(lat1) == int or type(lat1) == float), "Latitude 1 is not of accepted numeric type"
    assert (-90 <= lat1 <= 90), "Invalid latitude 1 given (should be in range -90 to 90)"
    assert (type(lon1) == int or type(lon1) == float), "Longitude 1 is not of accepted numeric type"
    assert (-180 <= lon1 <= 180), "Invalid longitude 1 given (should be in range -180 to 180)"

    assert (type(lat2) == int or type(lat2) == float), "Latitude 2 is not of accepted numeric type"
    assert (-90 <= lat2 <= 90), "Invalid latitude 2 given (should be in range -90 to 90)"
    assert (type(lon2) == int or type(lon2) == float), "Longitude 2 is not of accepted numeric type"
    assert (-180 <= lon2 <= 180), "Invalid longitude 2 given (should be in range -180 to 180)"

    R = 6371
    inner = pow(sin((lat2 - lat1) / 2), 2) + cos(lat1) * cos(lat2) * pow(sin((lon2 - lon1) / 2), 2)
    d = 2 * R * asin(sqrt(inner))

    return d
