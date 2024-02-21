import os
import py_vncorenlp
from transformers import AutoModel, AutoTokenizer
from underthesea import word_tokenize

from typing import List, Text, Dict, Any
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.shared.nlu.training_data.message import Message
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
from rasa.engine.graph import ExecutionContext


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)
class ViTokenizer(Tokenizer):
    @staticmethod
    def supported_languages() -> List[str]:
        return ["vi"]  # Only support Vietnamese language

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,
            # Symbol on which intent should be split
            "intent_split_symbol": "_",
            # Regular expression to detect tokens
            "token_pattern": None,
            # Symbol on which prefix should be split
            "prefix_separator_symbol": None,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        super().__init__(config)

        # # Download VnCoreNLP model if not exists
        vncorenlp_path = os.getenv("VNCORENLP_PATH", "vncorenlp")
        # # py_vncorenlp.download_model(model_path)

        # # Load VnCoreNLP model
        self.tokenizer = py_vncorenlp.VnCoreNLP(
            annotators=["wseg"], save_dir=vncorenlp_path
        )
        # self.tokenizer = word_tokenize

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> Tokenizer:
        return cls(config)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        # words = self.tokenizer(text)
        words = self.tokenizer.word_segment(text)[0].split()

        # # Remove underscore from word
        words = [word.replace("_", " ") for word in words]
        tokens = self._convert_words_to_tokens(words, text)

        return self._apply_token_pattern(tokens)
