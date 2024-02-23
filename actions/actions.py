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
from actions.normalizers import normalize_district


class ValidateSearchPropertiesFrom(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_properties_form"

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
        return []
