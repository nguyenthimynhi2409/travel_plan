import os
import requests

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "google-maps-places.p.rapidapi.com")


def get_places_nearby(city: str, category: str = "tourist_attraction", limit: int = 5):
    url = f"https://{RAPIDAPI_HOST}/maps/api/place/nearbysearch/json"
    query = {"location": _get_city_center(city), "radius": "5000", "type": category}
    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}
    resp = requests.get(url, headers=headers, params=query)
    data = resp.json()
    results = []
    for p in data.get("results", [])[:limit]:
        results.append(
            {
                "name": p.get("name"),
                "address": p.get("vicinity"),
                "rating": p.get("rating"),
                "user_ratings_total": p.get("user_ratings_total"),
            }
        )
    return results


def _get_city_center(city: str):
    city_map = {
        "Tokyo": "35.6895,139.6917",
        "Bangkok": "13.7563,100.5018",
        "Paris": "48.8566,2.3522",
        "Singapore": "1.3521,103.8198",
    }
    return city_map.get(city, "0,0")
