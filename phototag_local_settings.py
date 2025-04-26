import anchorpoint as ap
import apsync as aps
from phototag_settings import PhototagSettings
from typing import Optional


class PhototagLocalSettings:
    def __init__(self):
        self.settings = aps.Settings(
            ap.get_context().workspace_id, f"phototag_ai_local_settings"
        )
        self.load()
    
    # Local settings
    last_selected: Optional[str]
    last_edited: Optional[str]
    section_keywords_folded: bool
    section_description_folded: bool
    section_title_folded: bool
    section_additional_folded: bool
    section_ai_attributes_folded: bool

    def get(self, key: str, default: object = "") -> object:
        return self.settings.get(key, default)

    def set(self, key: str, value: object):
        self.settings.set(key, value)

    def load(self):
        """
        Loads the settings from the Settings.
        """
        self.last_selected = self.get("last_selected")
        self.last_edited = self.get("last_edited")
        self.section_keywords_folded = bool(self.get("section_keywords_folded", True))
        self.section_description_folded = bool(self.get("section_description_folded", True))
        self.section_title_folded = bool(self.get("section_title_folded", True))
        self.section_additional_folded = bool(self.get("section_additional_folded", True))
        self.section_ai_attributes_folded = bool(self.get("section_ai_attributes_folded", True))

    def store(self):
        """
        Stores the settings in the Settings.
        """
        self.set("last_selected", self.last_selected)
        self.set("last_edited", self.last_edited)
        self.set("section_keywords_folded", self.section_keywords_folded)
        self.set("section_description_folded", self.section_description_folded)
        self.set("section_title_folded", self.section_title_folded)
        self.set("section_additional_folded", self.section_additional_folded)
        self.set("section_ai_attributes_folded", self.section_ai_attributes_folded)
        self.settings.store()
