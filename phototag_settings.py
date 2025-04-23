import apsync as aps
import anchorpoint as ap
from typing import Optional


class PhototagSettings:
    def __init__(self, name: str = "default"):
        self.name = name
        self.local_settings = aps.SharedSettings(
            ap.get_context().workspace_id, f"phototag_ai_{name}"
        )
        self.load()

    def get(self, key: str, default: object = "") -> object:
        return self.local_settings.get(key, default)

    def set(self, key: str, value: object):
        self.local_settings.set(key, value)

    # Phototag.ai settings
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

    # Attribute settings
    enable_ai_title: bool
    enable_ai_description: bool
    enable_ai_tags: bool

    def load(self):
        """
        Loads the settings from the SharedSettings.
        """
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
        self.use_file_name_for_context = bool(
            self.get("use_file_name_for_context", True)
        )
        self.single_word_keywords_only = bool(
            self.get("single_word_keywords_only", False)
        )
        self.be_creative = bool(self.get("be_creative", False))
        self.title_case_title = bool(self.get("title_case_title", True))

        self.enable_ai_title = bool(self.get("enable_ai_title", True))
        self.enable_ai_description = bool(self.get("enable_ai_description", True))
        self.enable_ai_tags = bool(self.get("enable_ai_tags", True))

    def store(self):
        """
        Stores the settings in the SharedSettings.
        """
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

        self.set("enable_ai_title", self.enable_ai_title)
        self.set("enable_ai_description", self.enable_ai_description)
        self.set("enable_ai_tags", self.enable_ai_tags)

        self.local_settings.store()

    def rename(self, new_name: str):
        """
        Renames the settings and updates the SharedSettings.
        """
        old_settings = self.local_settings
        self.name = new_name
        self.local_settings = aps.SharedSettings(
            ap.get_context().workspace_id, f"phototag_ai_{new_name}"
        )
        self.store()
