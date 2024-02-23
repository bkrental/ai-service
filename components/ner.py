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


def convert_to_rasa_format(entities: List[Dict[Text, Any]]) -> List[Dict[Text, Any]]:
    rasa_entities = []
    current_entity = None
    current_entity_text = ""
    for entity in entities:
        if entity["entity"].startswith("B-"):
            if current_entity is not None:
                rasa_entities.append(
                    {
                        "start": current_entity["start"],
                        "end": current_entity["end"],
                        "value": current_entity_text,
                        "entity": current_entity["entity"][2:].lower(),
                        "confidence_entity": str(current_entity["score"]),
                    }
                )
            current_entity = entity
            current_entity_text = entity["word"]
        elif entity["entity"].startswith("I-"):
            if current_entity is not None:
                current_entity_text += " " + entity["word"]
                current_entity["end"] = entity["end"]
                current_entity["score"] = min(current_entity["score"], entity["score"])
        else:
            # Invalid entity format, skip
            pass

    if current_entity is not None:
        rasa_entities.append(
            {
                "start": current_entity["start"],
                "end": current_entity["end"],
                "value": current_entity_text,
                "entity": current_entity["entity"][2:].lower(),
                "confidence_entity": str(current_entity["score"]),
            }
        )
    return rasa_entities


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False
)
class HUSTEntityExtractor(GraphComponent, EntityExtractorMixin):
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {"dimensions": ["LOCATION", "ORGANIZATION"], "threshold": 0.5}

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> HUSTEntityExtractor:
        return cls(config)

    def __init__(self, config: Dict[Text, Any]) -> None:
        model_name = "NlpHUST/ner-vietnamese-electra-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)

        self.nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        self.component_config = config

    @staticmethod
    def filter_irrelevant_entities(entities: list, dimensions, threshold=0.5) -> list:
        extracted = []
        for entity in entities:
            if (
                entity["entity"] in dimensions
                and float(entity["confidence_entity"]) > threshold
            ):
                extracted.append(entity)
        return extracted

    def process(self, messages: List[Message]) -> List[Message]:
        threshold = self.component_config["threshold"]
        dimensions = self.component_config["dimensions"]

        for message in messages:
            matches = self.nlp(message.get(TEXT))
            all_extracted = convert_to_rasa_format(matches)
            extracted = self.filter_irrelevant_entities(
                all_extracted, dimensions, threshold
            )
            extracted = self.add_extractor_name(extracted)
            message.set(
                ENTITIES, message.get(ENTITIES, []) + extracted, add_to_output=True
            )

        return messages
