import apsync as aps
from typing import Optional

class PhototagSettings:
    def __init__(self):
        self.local_settings = aps.Settings("phototag_ai")
        self.load()

    def get(self, key: str, default: object = "") -> object:
        return self.local_settings.get(key, default)

    def set(self, key: str, value: object):
        self.local_settings.set(key, value)

    phototag_api_key: str
    max_keywords: Optional[int]
    min_keywords: Optional[int]
    required_keywords: Optional[str]
    excluded_keywords: Optional[str]
    custom_context: Optional[str]
    prohibited_characters: Optional[str]
    max_description_chars: Optional[int]
    min_description_chars: Optional[int]
    max_title_chars: Optional[int]
    min_title_chars: Optional[int]
    use_file_name_for_context: bool
    single_word_keywords_only: bool
    be_creative: bool
    title_case_title: bool

    def load(self):
        self.phototag_api_key = str(self.get("phototag_api_key"))
        self.max_keywords = self.get("max_keywords")
        self.min_keywords = self.get("min_keywords")
        self.required_keywords = self.get("required_keywords")
        self.excluded_keywords = self.get("excluded_keywords")
        self.custom_context = self.get("custom_context")
        self.prohibited_characters = self.get("prohibited_characters")
        self.max_description_chars = self.get("max_description_chars")
        self.min_description_chars = self.get("min_description_chars")
        self.max_title_chars = self.get("max_title_chars")
        self.min_title_chars = self.get("min_title_chars")
        self.use_file_name_for_context = bool(self.get("use_file_name_for_context", True))
        self.single_word_keywords_only = bool(self.get("single_word_keywords_only", False))
        self.be_creative = bool(self.get("be_creative", False))
        self.title_case_title = bool(self.get("title_case_title", True))

    def store(self):
        self.set("phototag_api_key", self.phototag_api_key)
        self.set("max_keywords", self.max_keywords)
        self.set("min_keywords", self.min_keywords)
        self.set("required_keywords", self.required_keywords)
        self.set("excluded_keywords", self.excluded_keywords)
        self.set("custom_context", self.custom_context)
        self.set("prohibited_characters", self.prohibited_characters)
        self.set("max_description_chars", self.max_description_chars)
        self.set("min_description_chars", self.min_description_chars)
        self.set("max_title_chars", self.max_title_chars)
        self.set("min_title_chars", self.min_title_chars)
        self.set("use_file_name_for_context", self.use_file_name_for_context)
        self.set("single_word_keywords_only", self.single_word_keywords_only)
        self.set("be_creative", self.be_creative)
        self.set("title_case_title", self.title_case_title)
        self.local_settings.store() 