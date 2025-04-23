import anchorpoint as ap
import apsync as aps
import os
from typing import Optional
from phototag_settings import PhototagSettings
from phototag_settings_list import PhototagSettingsList

settings_list = PhototagSettingsList()
current_settings = PhototagSettings()

# Dialog variables
new_settings_dialog = None
rename_settings_dialog = None
load_settings_dialog = None
settings_dialog = None


def delete_api_key_callback(dialog: ap.Dialog):
    """
    Deletes the Phototag API key and updates the settings list.
    """
    settings_list.set_api_key("")
    dialog.set_value("phototag_api_key", "")


def validate_int_range(value: str, min_val: int, max_val: int) -> bool:
    """
    Validates if the input value is an integer and within the specified range.
    """
    try:
        num = int(value)
        return min_val <= num <= max_val
    except ValueError:
        return False


def new_settings_callback(dialog: ap.Dialog):
    """
    Creates a new Phototag settings and updates the settings list.
    """
    name = dialog.get_value("settings_name")
    if not name:
        ap.UI().show_error("Settings name cannot be empty")
        return

    if settings_list.add_setting(name):
        global current_settings
        current_settings = PhototagSettings(name)
        show_settings_dialog()
    else:
        ap.UI().show_error("Settings with this name already exists")


def show_new_settings_dialog():
    """
    Displays a dialog to create a new Phototag settings.
    """
    global new_settings_dialog
    new_settings_dialog = ap.Dialog()
    new_settings_dialog.closable = False
    new_settings_dialog.title = "New Settings"
    new_settings_dialog.add_text("Settings Name:")
    new_settings_dialog.add_input("", var="settings_name", width=200)
    (
        new_settings_dialog.add_button(
            "Cancel", callback=lambda _: show_settings_dialog(), primary=False
        ).add_button("Create", callback=new_settings_callback)
    )
    new_settings_dialog.show()


def rename_settings_callback(dialog: ap.Dialog):
    """
    Renames a Phototag settings and updates the settings list.
    """
    new_name = dialog.get_value("settings_name")
    if not new_name:
        ap.UI().show_error("Settings name cannot be empty")
        return

    if new_name in settings_list.get_settings_names():
        ap.UI().show_error("Settings with this name already exists")
        return

    settings_list.rename_setting(current_settings.name, new_name)
    current_settings.rename(new_name)
    show_settings_dialog()


def show_rename_settings_dialog():
    """
    Displays a dialog to rename a Phototag settings.
    """
    global rename_settings_dialog
    rename_settings_dialog = ap.Dialog()
    rename_settings_dialog.closable = False
    rename_settings_dialog.title = "Rename Settings"
    rename_settings_dialog.add_text("New Settings Name:")
    rename_settings_dialog.add_input(
        current_settings.name, var="settings_name", width=200
    )
    (
        rename_settings_dialog.add_button(
            "Cancel", callback=lambda _: show_settings_dialog(), primary=False
        ).add_button("Rename", callback=rename_settings_callback)
    )
    rename_settings_dialog.show()


def load_settings_callback(dialog: ap.Dialog):
    """
    Loads a Phototag settings and updates the current settings.
    """
    name = dialog.get_value("settings_name")
    global current_settings
    current_settings = settings_list.get_setting(name)
    if current_settings:
        show_settings_dialog()
    else:
        ap.UI().show_error("Failed to load settings")


def show_load_settings_dialog():
    """
    Displays a dialog to load a Phototag settings.
    """
    global load_settings_dialog
    load_settings_dialog = ap.Dialog()
    load_settings_dialog.closable = False
    load_settings_dialog.title = "Load Settings"
    names = settings_list.get_settings_names()
    if not names:
        ap.UI().show_error("No saved settings found")
        return

    load_settings_dialog.add_text("Select Settings:").add_dropdown(
        names[0], names, var="settings_name"
    )
    (
        load_settings_dialog.add_button(
            "Cancel", callback=lambda _: show_settings_dialog(), primary=False
        ).add_button("Load", callback=load_settings_callback)
    )
    load_settings_dialog.show()


def save_settings_callback(dialog: ap.Dialog):
    """
    Saves the current Phototag settings.
    """
    if current_settings.name == "default":
        show_new_settings_dialog()
        return

    current_settings.store()
    ap.UI().show_success("Settings Saved")


def apply_callback(dialog: ap.Dialog):
    """
    Applies the current Phototag settings.
    """
    # Store API key
    settings_list.set_api_key(str(dialog.get_value("phototag_api_key")))

    # Keywords settings
    max_keywords = dialog.get_value("max_keywords")
    if max_keywords and not validate_int_range(max_keywords, 5, 200):
        ap.UI().show_error("Max Keywords must be between 5 and 200")
        return

    min_keywords = dialog.get_value("min_keywords")
    if min_keywords and not validate_int_range(min_keywords, 5, 40):
        ap.UI().show_error("Min Keywords must be between 5 and 40")
        return

    # Description settings
    max_desc = dialog.get_value("max_description_chars")
    if max_desc and not validate_int_range(max_desc, 50, 500):
        ap.UI().show_error("Max Description Characters must be between 50 and 500")
        return

    min_desc = dialog.get_value("min_description_chars")
    if min_desc and not validate_int_range(min_desc, 5, 200):
        ap.UI().show_error("Min Description Characters must be between 5 and 200")
        return

    # Title settings
    max_title = dialog.get_value("max_title_chars")
    if max_title and not validate_int_range(max_title, 50, 500):
        ap.UI().show_error("Max Title Characters must be between 50 and 500")
        return

    min_title = dialog.get_value("min_title_chars")
    if min_title and not validate_int_range(min_title, 5, 200):
        ap.UI().show_error("Min Title Characters must be between 5 and 200")
        return

    # Store settings
    current_settings.max_keywords = int(max_keywords) if max_keywords else 0
    current_settings.min_keywords = int(min_keywords) if min_keywords else 0
    current_settings.required_keywords = str(
        dialog.get_value("required_keywords") or ""
    )
    current_settings.excluded_keywords = str(
        dialog.get_value("excluded_keywords") or ""
    )
    current_settings.custom_context = str(dialog.get_value("custom_context") or "")
    current_settings.prohibited_characters = str(
        dialog.get_value("prohibited_characters") or ""
    )
    current_settings.max_description_chars = int(max_desc) if max_desc else 0
    current_settings.min_description_chars = int(min_desc) if min_desc else 0
    current_settings.max_title_chars = int(max_title) if max_title else 0
    current_settings.min_title_chars = int(min_title) if min_title else 0
    current_settings.use_file_name_for_context = bool(
        dialog.get_value("use_file_name_for_context")
    )
    current_settings.single_word_keywords_only = bool(
        dialog.get_value("single_word_keywords_only")
    )
    current_settings.be_creative = bool(dialog.get_value("be_creative"))
    current_settings.title_case_title = bool(dialog.get_value("title_case_title"))

    current_settings.enable_ai_title = bool(dialog.get_value("enable_ai_title"))
    current_settings.enable_ai_description = bool(
        dialog.get_value("enable_ai_description")
    )
    current_settings.enable_ai_tags = bool(dialog.get_value("enable_ai_tags"))

    current_settings.store()
    ap.UI().show_success("Settings Updated")
    dialog.close()


def show_settings_dialog():
    """
    Displays a dialog to manage Phototag settings.
    """
    global settings_dialog
    label_width = 292
    input_width_small = 100
    input_width_large = 400

    settings_dialog = ap.Dialog()
    settings_dialog.title = f"Phototag.ai Settings - {current_settings.name}"
    ctx = ap.get_context()
    if ctx.icon:
        settings_dialog.icon = ctx.icon

    # Settings Management
    settings_dialog.add_text("<b>Settings Management</b>")
    settings_dialog.add_text(f"Current Settings: {current_settings.name}")
    (
        settings_dialog.add_button(
            "New Settings", callback=lambda _: show_new_settings_dialog()
        )
        .add_button("Load Settings", callback=lambda _: show_load_settings_dialog())
        .add_button("Save Settings", callback=save_settings_callback)
        .add_button("Rename Settings", callback=lambda _: show_rename_settings_dialog())
    )
    settings_dialog.add_separator()

    # API Key Section
    settings_dialog.add_text("<b>Phototag.ai API Key</b>")
    settings_dialog.add_input(
        settings_list.get_api_key(),
        var="phototag_api_key",
        width=input_width_large,
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        password=True,
    ).add_button("Delete", callback=delete_api_key_callback)
    settings_dialog.add_info(
        "An API key is required to access Phototag.ai services. Create an API key on "
        "<a href='https://phototag.ai'>the Phototag.ai website</a>."
    )
    settings_dialog.add_separator()

    # Keywords Section
    settings_dialog.start_section("Keywords Settings", folded=False)
    settings_dialog.add_text("Min Keywords:", width=label_width).add_input(
        str(current_settings.min_keywords or ""),
        var="min_keywords",
        width=input_width_small,
    )
    settings_dialog.add_info("Minimum number of keywords to return (range: 5-40)")
    settings_dialog.add_text("Max Keywords:", width=label_width).add_input(
        str(current_settings.max_keywords or ""),
        var="max_keywords",
        width=input_width_small,
    )
    settings_dialog.add_info(
        "Maximum number of keywords to return, overrides minKeywords (range: 5-200)"
    )
    settings_dialog.add_text("Required Keywords (comma-separated):")
    settings_dialog.add_input(
        current_settings.required_keywords or "",
        var="required_keywords",
        width=input_width_large,
    )
    settings_dialog.add_info("Comma-separated keywords that must be included")
    settings_dialog.add_text("Excluded Keywords (comma-separated):")
    settings_dialog.add_input(
        current_settings.excluded_keywords or "",
        var="excluded_keywords",
        width=input_width_large,
    )
    settings_dialog.add_info("Comma-separated keywords that must be excluded")
    settings_dialog.add_checkbox(
        current_settings.single_word_keywords_only,
        var="single_word_keywords_only",
        text="Single Word Keywords Only",
    )
    settings_dialog.add_info("Only allow single-word keywords")
    settings_dialog.end_section()

    # Description Section
    settings_dialog.start_section("Description Settings", folded=False)
    settings_dialog.add_text(
        "Min Description Characters:", width=label_width
    ).add_input(
        str(current_settings.min_description_chars or ""),
        var="min_description_chars",
        width=input_width_small,
    )
    settings_dialog.add_info(
        "Minimum number of characters allowed in the description (range: 5-200)"
    )
    settings_dialog.add_text(
        "Max Description Characters:", width=label_width
    ).add_input(
        str(current_settings.max_description_chars or ""),
        var="max_description_chars",
        width=input_width_small,
    )
    settings_dialog.add_info(
        "Maximum number of characters allowed in the description, overrides minDescription (range: 50-500)"
    )
    settings_dialog.end_section()

    # Title Section
    settings_dialog.start_section("Title Settings", folded=False)
    settings_dialog.add_text("Min Title Characters:", width=label_width).add_input(
        str(current_settings.min_title_chars or ""),
        var="min_title_chars",
        width=input_width_small,
    )
    settings_dialog.add_info(
        "Minimum number of characters allowed in the title (range: 5-200)"
    )
    settings_dialog.add_text("Max Title Characters:", width=label_width).add_input(
        str(current_settings.max_title_chars or ""),
        var="max_title_chars",
        width=input_width_small,
    )
    settings_dialog.add_info(
        "Maximum number of characters allowed in the title, overrides minTitle (range: 50-500)"
    )
    settings_dialog.add_checkbox(
        current_settings.title_case_title,
        var="title_case_title",
        text="Title Case Title",
    )
    settings_dialog.add_info("Use title case capitalization for the title")
    settings_dialog.end_section()

    # Additional Settings
    settings_dialog.start_section("Additional Settings", folded=False)
    settings_dialog.add_text("Custom Context:")
    settings_dialog.add_input(
        current_settings.custom_context or "",
        var="custom_context",
        width=input_width_large,
    )
    settings_dialog.add_info("Additional context for keyword generation")
    settings_dialog.add_text("Prohibited Characters:")
    settings_dialog.add_input(
        current_settings.prohibited_characters or "",
        var="prohibited_characters",
        width=input_width_large,
    )
    settings_dialog.add_info(
        "Characters to be removed from the title, description, and keywords"
    )
    settings_dialog.add_checkbox(
        current_settings.use_file_name_for_context,
        var="use_file_name_for_context",
        text="Use File Name for Context",
    )
    settings_dialog.add_info("Use the file name as context for keyword generation")
    settings_dialog.add_checkbox(
        current_settings.be_creative, var="be_creative", text="Be Creative"
    )
    settings_dialog.add_info(
        "Make the title and description more creative and artistic"
    )
    settings_dialog.end_section()

    # AI Attributes Section
    settings_dialog.start_section("AI Attributes", folded=False)
    settings_dialog.add_checkbox(
        current_settings.enable_ai_title, var="enable_ai_title", text="Enable AI-Title"
    )
    settings_dialog.add_info("Generate and apply AI-generated titles")
    settings_dialog.add_checkbox(
        current_settings.enable_ai_description,
        var="enable_ai_description",
        text="Enable AI-Description",
    )
    settings_dialog.add_info("Generate and apply AI-generated descriptions")
    settings_dialog.add_checkbox(
        current_settings.enable_ai_tags, var="enable_ai_tags", text="Enable AI-Tags"
    )
    settings_dialog.add_info("Generate and apply AI-generated tags")
    settings_dialog.end_section()

    settings_dialog.add_button("Apply", callback=apply_callback)
    settings_dialog.show()


def main():
    show_settings_dialog()


if __name__ == "__main__":
    main()
