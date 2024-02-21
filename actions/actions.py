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

        properties = self.get_properties()

        dispatcher.utter_message(
            text=f"Đây là kết quả các {property_type} có giá từ {price_lower_bound} đến {price_upper_bound}"
        )
        return []
