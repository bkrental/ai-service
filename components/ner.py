from __future__ import annotations
import time
import json
import logging
import os
import requests
from typing import Any, List, Optional, Text, Dict
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

import rasa.utils.endpoints as endpoints_utils
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.constants import DOCS_URL_COMPONENTS
from rasa.shared.nlu.constants import ENTITIES, TEXT
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.nlu.training_data.message import Message
import rasa.shared.utils.io


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False
)
class LocationExtractor(GraphComponent, EntityExtractorMixin):
    @staticmethod
    def required_packages() -> List[Text]:
        return []

    @staticmethod
    def create(
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> LocationExtractor:
        return LocationExtractor()

    def __init__(self) -> None:
        tokenizer = AutoTokenizer.from_pretrained("NlpHUST/ner-vietnamese-electra-base")
        model = AutoModelForTokenClassification.from_pretrained(
            "NlpHUST/ner-vietnamese-electra-base"
        )
        self.nlp = pipeline("ner", model=model, tokenizer=tokenizer)

    def process(self, message: Message, **kwargs: Any) -> None:
        if TEXT in message.data:
            response = requests.post(self.url, json={"text": message.data[TEXT]})
            response.raise_for_status()
            extracted = response.json()
            entities = message.get(ENTITIES, []) + extracted
            message.set(ENTITIES, entities, add_to_output=True)
