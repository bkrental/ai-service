import os
import requests
import json
import textwrap

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Coroutine, Text, Dict, List

from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset, Restarted, FollowupAction
from actions.constants import SUPPORTED_PROPERTY_TYPES
from actions.extractor import extract_location, extract_price_slot
from actions.load_env import load_environment_variables
from actions.normalizers import normalize_price

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

from actions.utils import extract_text_from_bio

load_environment_variables()
GOONGJS_API_KEY = os.getenv("GOONGJS_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
RENTAL_SERVICE_URL = os.getenv("RENTAL_SERVICE_URL")

class ActionBye(Action):
    def name(self) -> Text:
        return "action_bye"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        dispatcher.utter_message(text="Tạm biệt, rất vui được hỗ trợ bạn")
        return [AllSlotsReset(), Restarted()]

class ActionCheckForPriceUpdate(Action):
    def name(self) -> Text:
        return "action_check_for_price_update"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])
        price_range = extract_price_slot(entities)
        # If the price slot is updated, re-trigger the form
        if price_range:
            dispatcher.utter_message(text="Bạn vừa cập nhập lại khoảng giá, tôi sẽ tìm kiếm lại cho bạn")
            return [FollowupAction("search_properties_form")]
        
        return []

class ActionCheckForLocationUpdate(Action):
    def name(self) -> Text:
        return "action_check_for_location_update"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Tôi sẽ tìm kiếm lại cho bạn với vị trí mới cập nhập")
        return [FollowupAction("search_properties_form")]
        
        return []


class ValidateSearchPropertiesFrom(FormValidationAction):
    def __init__(self):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("NlpHUST/ner-vietnamese-electra-base")
        self.model = AutoModelForTokenClassification.from_pretrained("NlpHUST/ner-vietnamese-electra-base")
        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

    def name(self) -> Text:
        return "validate_search_properties_form"

    def extract_price(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        entities = tracker.latest_message.get("entities", [])

        price_range = extract_price_slot(entities)
        return {"price": price_range} if price_range else {}
    
    def extract_location( self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        latest_message = tracker.latest_message['text']

        location = extract_location(latest_message, self.nlp)
        return {"location": location} if location else {}

    def validate_price(
        self, slot_value, dispatcher, tracker, domain
    ) -> Dict[Text, Any]:

        print(slot_value)

        return {"price": slot_value}

    def validate_property_type(self, slot_value, dispatcher: CollectingDispatcher, tracker, domain) -> Dict[Text, Any]:
        if not slot_value in SUPPORTED_PROPERTY_TYPES:
            dispatcher.utter_message("Xin lỗi, loại bất động sản bạn nhập không được hỗ trợ")
            return {"property_type": None}

        return {"property_type": slot_value}

class ActionSearchProperties(Action):
    def name(self) -> Text:
        return "action_submit_search_properties_form"

    def get_post_card_json(self, post):
        return {
            "title": post["name"],
            "image_url": post["thumbnail"],
            "subtitle": post["displayed_address"] + "\n" + str(post["price"]) + " triệu/tháng",
            "buttons": [
                {
                    "type": "web_url",
                    "url": f"{FRONTEND_URL}/posts/{post['_id']}",
                    "title": "Xem trên web",
                },
                {
                    "type":"postback",
                    "title": "Thông tin chi tiết",
                    "payload": "/view_post_details " + json.dumps({"post_id": post["_id"]})
                }
            ],
        }

    def run(self, dispatcher, tracker, domain):

        property_type = tracker.get_slot("property_type")
        transaction_type = tracker.get_slot("transaction_type")
        [bp, tp] = tracker.get_slot("price")
        location = tracker.get_slot("location")

        print(property_type, transaction_type, bp, tp, location)

        params = dict()
        if property_type:
            params["pt"] = property_type
        
        if bp:
            params["bp"] = bp
        
        if tp:
            params["tp"] = tp
        
        if transaction_type and transaction_type in ["rent", "buy"]:
            params["transaction"] = transaction_type
        
        if location and len(location) == 2:
            [lng, lat] = location
            params["center"] = f"{lng},{lat}"
        elif location and len(location) == 1:
            print("Search using boundary")
            [boundary] = location
            params["boundary"] = boundary

        url = f"{RENTAL_SERVICE_URL}/posts"
        response = requests.get(url, params=params)

        if response.status_code != 200:
            dispatcher.utter_message(
                "Có lỗi xảy ra, xin vui lòng thử lại sau"
            )
            return
        
        data = response.json()["data"]
        print(data)

        if not data or len(data) == 0:
            dispatcher.utter_message(
                "Xin lỗi tôi không thể tìm thấy các bất động sản phù hợp với yêu cầu của bạn"
            )
            return

        elements = list(
            map(
                lambda post: self.get_post_card_json(post),
                data,
            )
        )

        gt = {
            "attachment": {
                "type": "template",
                "payload": {"template_type": "generic", "elements": elements},
            }
        }
        dispatcher.utter_message(json_message=gt)

class ActionViewPostDetails(Action):
    def name(self) -> Text:
        return "action_view_post_details"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        data = json.loads(tracker.latest_message["text"].split("/view_post_details ")[1])
        post_id = data["post_id"]

        if not post_id:
            dispatcher.utter_message(text="Sorry, I couldn't find the post details.")
            return []

        url = f"{RENTAL_SERVICE_URL}/posts/{post_id}"
        response = requests.get(url)

        if response.status_code != 200:
            dispatcher.utter_message(
                "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết của bài đăng này"
            )
            return

        data = response.json()["data"]
        post = data["post"]

        message = textwrap.dedent(f"""
            Sau đây là thông tin chi tiết cho bài post: {post["name"]}

            Address: {post["displayed_address"]}

            Price: {post["price"]} triệu

            Contact: {post.get("contact").get("name")} - {post.get("contact").get("phone")}

            {post["description"]}
        """)
        dispatcher.utter_message(text=message)
        return

