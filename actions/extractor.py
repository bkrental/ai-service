import os
import requests
from actions.normalizers import normalize_price
from actions.utils import extract_text_from_bio

def extract_price_slot(entities):
    price_range = [None, None]
    is_updated = False

    for entity in entities:
        if entity.get("entity") == "price":
            price_value = normalize_price(entity.get("value"))
            role = entity.get("role")
            if role == "average":
                price_range = (price_value * 0.8, price_value * 1.2)
                return price_range

            if role == "top":
                is_updated = True
                price_range[1] = price_value

            elif role == "bottom":
                is_updated = True
                price_range[0] = price_value

    return price_range if is_updated else None

def extract_location(message, ner_model):
    entities = ner_model(message)
    addresses = extract_text_from_bio(entities)

    if len(addresses) == 0: return None
    address = " ".join(addresses)

    url = f"https://rsapi.goong.io/geocode"

    params = dict()
    params["address"] = address
    params["api_key"] = os.getenv("GOONGJS_API_KEY")
    response = requests.get(url, params=params)

    if response.status_code != 200: return

    data = response.json()
    if data.get("results") and len(data.get("results")) > 0:
        geometry = (data.get("results")[0].get("geometry"))
        if geometry.get("boundary"):
            boundary = geometry.get("boundary")
            return [boundary]

        result = data.get("results")[0].get("geometry").get("location")
        return  [result.get("lng"), result.get("lat")]


    

