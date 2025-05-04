import apsync as aps
import anchorpoint as ap
from typing import Optional, List
from phototag_settings import PhototagSettings


class PhototagSettingsList:
    def __init__(self):
        self.shared_settings = aps.SharedSettings(
            ap.get_context().workspace_id, "phototag_ai_list"
        )
        self.settings_names = self.shared_settings.get("settings_names", [])
        # add default settings
        if "default" not in self.settings_names:
            self.settings_names.append("default")
        self.phototag_api_key = str(self.shared_settings.get("phototag_api_key", ""))
        self.enabled_for_members = bool(
            self.shared_settings.get("enabled_for_members", True)
        )

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
            self.shared_settings.set("settings_names", self.settings_names)
            self.shared_settings.store()
            self.__update_default_setting__()
            return True
        return False

    def __update_default_setting__(self):
        if "default" not in self.settings_names:
            self.settings_names.append("default")
            self.shared_settings.set("settings_names", self.settings_names)
            self.shared_settings.store()

    def delete_setting(self, name: str) -> bool:
        """
        Deletes a setting with the given name and its associated data.
        """
        if name in self.settings_names:
            # Delete the settings data
            settings = PhototagSettings(name)
            settings.delete()
            # Remove from list
            self.settings_names.remove(name)
            self.shared_settings.set("settings_names", self.settings_names)
            self.shared_settings.store()
            self.__update_default_setting__()
            return True
        return False

    def rename_setting(self, old_name: str, new_name: str) -> bool:
        """
        Renames a setting with the given name.
        """
        if old_name not in self.settings_names:
            ap.UI().show_error(f"Settings with name {old_name} not found")
            return False

        if new_name in self.settings_names:
            ap.UI().show_error(f"Settings with name {new_name} already exists")
            return False

        index = self.settings_names.index(old_name)
        self.settings_names[index] = new_name
        self.shared_settings.set("settings_names", self.settings_names)
        self.shared_settings.store()
        self.__update_default_setting__()
        return True

    def set_api_key(self, key: str):
        """
        Sets the Phototag API key.
        """
        self.phototag_api_key = key
        self.shared_settings.set("phototag_api_key", key)
        self.shared_settings.store()

    def get_api_key(self) -> str:
        """
        Returns the Phototag API key.
        """
        return self.phototag_api_key

    def set_enabled_for_members(self, enabled: bool):
        """
        Sets whether Phototag is enabled for users.
        """
        self.enabled_for_members = enabled
        self.shared_settings.set("enabled_for_members", enabled)
        self.shared_settings.store()

    def get_enabled_for_members(self) -> bool:
        """
        Returns whether Phototag is enabled for users.
        """
        return self.enabled_for_members
