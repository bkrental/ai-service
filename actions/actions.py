# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List


class ActionSearchProperties(Action):
    def name(self) -> Text:
        return "action_search_properties"

    def run(self, dispatcher, tracker, domain):

        property_type = tracker.get_slot("property_type")
        price_lower_bound = tracker.get_slot("price_lower_bound")
        price_upper_bound = tracker.get_slot("price_upper_bound")

        res = requests.get("https://prod-backend.datnguyen2409.me/posts")

        if res.status_code != 200:
            return dispatcher.utter_message(response="utter_search_properties_error")

        properties_title = map(lambda p: p["name"], res.json()["data"])

        # dispatcher.utter_message(
        #     response="utter_search_properties",
        #     properties="\n".join(properties_title),
        # )

        dispatcher.utter_message(
            text=f"Đây là kết quả các {property_type} có giá từ {price_lower_bound} đến {price_upper_bound}"
        )
        return []
