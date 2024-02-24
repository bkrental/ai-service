import re
from thefuzz import fuzz
from unidecode import unidecode


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


def normalize_district(district_pred: str) -> str:
    district_pred = district_pred.lower()
    district_prefixes = {
        "Quận": ["quan ", "quận ", "q"],
        "Huyện": ["huyen ", "huyện ", "h"],
        "Thành phố": ["thanh pho ", "thành phố ", "tp "],
    }

    district_aliases = []
    for prefix, aliases in district_prefixes.items():
        district_aliases += [(alias, prefix) for alias in aliases]

    # District name in the number format
    max_similarity_score = 70
    match = re.search(r"\d+", district_pred)
    if match is not None:
        district_number = match.group()

        most_similar_prefix = ""

        for alias, prefix in district_aliases:
            district_pattern = alias + district_number
            similarity_score_with_accents = fuzz.ratio(district_pred, district_pattern)

            if similarity_score_with_accents > max_similarity_score:
                most_similar_prefix = prefix
                max_similarity_score = similarity_score_with_accents

        return (
            most_similar_prefix + " " + district_number if most_similar_prefix else ""
        )

    # District name in the string format
    district_samples = [
        "Quận Bình Thạnh",
        "Quận Gò Vấp",
        "Quận Phú Nhuận",
        "Quận Tân Bình",
        "Huyện Bình Chánh",
        "Huyện Cần Giờ",
        "Huyện Củ Chi",
        "Huyện Hóc Môn",
        "Huyện Nhà Bè",
        "Thành phố Thủ Đức",
    ]

    most_similar_sample = ""
    for district_sample in district_samples:
        # Compare with accents
        similarity_score_with_accents = fuzz.ratio(
            district_pred, district_sample.lower()
        )

        # Compare without accents
        similarity_score_no_accents = fuzz.ratio(
            unidecode(district_pred), unidecode(district_sample.lower())
        )

        total_similarity_score = max(
            similarity_score_with_accents, similarity_score_no_accents
        )

        if total_similarity_score > max_similarity_score:
            max_similarity_score = total_similarity_score
            most_similar_sample = district_sample

    return most_similar_sample


print(normalize_price("20 tỷ, 1.5 triệu/thang"))
print(normalize_price("10 triệu/thang"))
print(normalize_price("30k"))
