import apsync as aps
import anchorpoint as ap
from typing import Optional, List
from phototag_settings import PhototagSettings


class PhototagSettingsList:
    def __init__(self):
        self.local_settings = aps.SharedSettings(
            ap.get_context().workspace_id, "phototag_ai_list"
        )
        self.settings_names = self.local_settings.get("settings_names", [])
        self.phototag_api_key = str(self.local_settings.get("phototag_api_key", ""))

    def get_settings_count(self) -> int:
        """
        Returns the number of saved settings.
        """
        return len(self.settings_names)

    def get_settings_names(self) -> List[str]:
        """
        Returns a list of all saved settings names.
        """
        return self.settings_names

    def get_setting(self, name: str) -> Optional[PhototagSettings]:
        """
        Returns a PhototagSettings object for the given name.
        """
        if name in self.settings_names:
            return PhototagSettings(name)
        return None

    def add_setting(self, name: str) -> bool:
        """
        Adds a new setting with the given name.
        """
        if name not in self.settings_names:
            self.settings_names.append(name)
            self.local_settings.set("settings_names", self.settings_names)
            self.local_settings.store()
            return True
        return False

    def remove_setting(self, name: str) -> bool:
        """
        Removes a setting with the given name.
        """
        if name in self.settings_names:
            self.settings_names.remove(name)
            self.local_settings.set("settings_names", self.settings_names)
            self.local_settings.store()
            return True
        return False

    def rename_setting(self, old_name: str, new_name: str) -> bool:
        """
        Renames a setting with the given name.
        """
        print(f"Renaming setting from {old_name} to {new_name}")
        if old_name not in self.settings_names:
            ap.UI().show_error(f"Settings with name {old_name} not found")
            return False

        if new_name in self.settings_names:
            ap.UI().show_error(f"Settings with name {new_name} already exists")
            return False

        index = self.settings_names.index(old_name)
        self.settings_names[index] = new_name
        self.local_settings.set("settings_names", self.settings_names)
        self.local_settings.store()
        return True

    def set_api_key(self, key: str):
        """
        Sets the Phototag API key.
        """
        self.phototag_api_key = key
        self.local_settings.set("phototag_api_key", key)
        self.local_settings.store()

    def get_api_key(self) -> str:
        """
        Returns the Phototag API key.
        """
        return self.phototag_api_key
