# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import requests

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

from rasa_sdk.types import DomainDict
from actions.normalizers import normalize_district, normalize_price


class ValidateSearchPropertiesFrom(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_properties_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        price_lower_bound = tracker.get_slot("price_lower_bound")
        price_upper_bound = tracker.get_slot("price_upper_bound")

        if price_lower_bound is not None and price_upper_bound is not None:
            if "price_average" in updated_slots:
                updated_slots.remove("price_average")

        return updated_slots

    def validate_price_lower_bound(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        price_lower_bound = normalize_price(slot_value)
        if price_lower_bound:
            tracker.slots["price_average"] = -1
            return {"price_lower_bound": price_lower_bound}

        return {"price_lower_bound": None}

    def validate_price_upper_bound(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        price_upper_bound = normalize_price(slot_value)
        if price_upper_bound:
            tracker.slots["price_average"] = -1
            return {"price_upper_bound": price_upper_bound}

        return {"price_upper_bound": None}

    def validate_price_average(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        average_price = normalize_price(slot_value)

        if average_price:
            lower_bound = average_price * 0.9
            upper_bound = average_price * 1.1

            # tracker.slots["price_lower_bound"] = lower_bound
            # tracker.slots["price_upper_bound"] = upper_bound
            return {
                "price_average": slot_value,
                "price_lower_bound": lower_bound,
                "price_upper_bound": upper_bound,
            }

        return {"price_average": None}

    def validate_districts(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print(slot_value)
        districts = set([normalize_district(district) for district in slot_value])
        districts = [district for district in districts if len(district) > 0]

        if len(districts) != 0:
            print(f"Form validated: {districts}")
            return {"districts": districts}

        return {"districts": None}


class ActionSearchProperties(Action):
    def name(self) -> Text:
        return "action_search_properties"

    def get_properties(self):
        res = requests.get("http://localhost:3000/posts")
        if res.status_code != 200:
            return None

        print(res.json()["data"])
        return res.json()["data"]

    def run(self, dispatcher, tracker, domain):

        property_type = tracker.get_slot("property_type")
        price_lower_bound = tracker.get_slot("price_lower_bound")
        price_upper_bound = tracker.get_slot("price_upper_bound")
        districts = ", ".join(tracker.get_slot("districts"))

        dispatcher.utter_message(
            text=f"Đây là kết quả các {property_type} tại {districts} có giá từ {price_lower_bound} đến {price_upper_bound}"
        )
