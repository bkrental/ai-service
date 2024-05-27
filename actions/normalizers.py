import re

def normalize_price(price: str) -> float:
    milion_regex = r"((\d+)(.\d+)?)(\s*(triệu|trieu|tr))"
    bilion_regex = r"((\d+)(.\d+)?)(\s*(tỷ|ty))"
    thousand_regex = r"((\d+)(.\d+)?)(\s*(nghìn|nghin|n|k))"

    bilion_match = re.search(bilion_regex, price.lower())
    milion_match = re.search(milion_regex, price.lower())
    thousand_match = re.search(thousand_regex, price.lower())

    bilion = float(bilion_match.group(1)) if bilion_match else 0
    milion = float(milion_match.group(1)) if milion_match else 0
    thousand = float(thousand_match.group(1)) if thousand_match else 0

    return bilion * 1000 + milion + thousand / 1000