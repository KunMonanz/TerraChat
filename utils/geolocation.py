import geoip2.database
from fastapi import Request

GEOIP_DB = "/GeoLite2-ASN.mmdb"


def get_location_from_ip(request: Request) -> str:
    client_ip = request.client.host
    try:
        with geoip2.database.Reader(GEOIP_DB) as reader:
            response = reader.city(client_ip)
            city = response.city.name or ""
            country = response.country.name or ""
            return f"{city}, {country}" if city else country
    except Exception:
        return "Unknown"
