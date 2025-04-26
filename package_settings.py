import anchorpoint as ap
import apsync as aps
import os
from typing import Optional
from phototag_settings import PhototagSettings
from phototag_settings_list import PhototagSettingsList
from phototag_api import get_phototag_credits
from phototag_local_settings import PhototagLocalSettings

settings_list = PhototagSettingsList()
current_settings = None
local_settings = PhototagLocalSettings()

# Initialize current_settings from last_edited if None
if current_settings is None and local_settings.last_edited:
    current_settings = PhototagSettings(local_settings.last_edited)
if current_settings is None:
    current_settings = PhototagSettings()

# Dialog variables
settings_dialog = None

keywords_section: ap.DialogEntry = None
description_section: ap.DialogEntry = None
title_section: ap.DialogEntry = None
additional_section: ap.DialogEntry = None
ai_attributes_section: ap.DialogEntry = None


def save_api_key_callback(dialog: ap.Dialog):
    """
    Saves the Phototag API key and updates the settings list.
    """
    api_key = str(dialog.get_value("phototag_api_key"))
    if not api_key:
        settings_list.set_api_key("")
        dialog.set_value("phototag_api_key", "")
    else:
        settings_list.set_api_key(api_key)
        check_credits_callback(dialog)
        ap.UI().show_success("API Key Updated")


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
        local_settings.last_edited = current_settings.name
        local_settings.store()
        show_settings_dialog()
    else:
        ap.UI().show_error("Settings with this name already exists")


def save_settings_callback(dialog: ap.Dialog):
    """
    Saves the current Phototag settings.
    """

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
    local_settings.last_edited = current_settings.name
    local_settings.store()

    ap.UI().show_success("Settings Saved")
    show_settings_dialog()


def settings_dropdown_callback(dialog: ap.Dialog, value: str):
    """
    Updates current settings when dropdown selection changes
    """
    name = value
    global current_settings
    current_settings = settings_list.get_setting(name)
    local_settings.last_edited = current_settings.name
    local_settings.store()
    show_settings_dialog()


def confirm_create_new_settings():
    """
    Creates new settings directly from the main dialog's input field
    """
    global settings_dialog, current_settings
    name = settings_dialog.get_value("create_new_field")
    if not name:
        ap.UI().show_error("Settings name cannot be empty")
        return

    if settings_list.add_setting(name):
        new_settings = PhototagSettings(name)
        new_settings.copy(current_settings)
        current_settings = new_settings
        local_settings.last_edited = current_settings.name
        local_settings.store()
        settings_dialog.hide_row("create_new_field", True)
        save_settings_callback(settings_dialog)
        show_settings_dialog()
    else:
        ap.UI().show_error("Settings with this name already exists")


def confirm_rename_settings():
    """
    Renames current settings directly from the main dialog's input field
    """
    global settings_dialog
    old_name = current_settings.name
    new_name = settings_dialog.get_value("rename_field")
    if not new_name:
        ap.UI().show_error("Settings name cannot be empty")
        return

    if old_name == new_name:
        settings_dialog.hide_row("rename_field", True)
        return

    if new_name in settings_list.get_settings_names():
        ap.UI().show_error("Settings with this name already exists")
        return

    settings_list.rename_setting(old_name, new_name)
    current_settings.rename(new_name)
    settings_dialog.hide_row("rename_field", True)
    show_settings_dialog()


def confirm_delete_settings():
    """
    Deletes the current settings after confirmation
    """
    global settings_dialog, current_settings
    name = current_settings.name
    if len(settings_list.get_settings_names()) <= 1:
        ap.UI().show_error("Cannot delete the last settings")
        return

    settings_list.delete_setting(name)
    current_settings = PhototagSettings(settings_list.get_settings_names()[0])
    local_settings.last_edited = current_settings.name
    local_settings.store()
    settings_dialog.hide_row("delete_confirm", True)
    show_settings_dialog()


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
    settings_dialog.icon = ctx.yaml_dir + "/icons/tagImage.svg"

    # API Key Section
    settings_dialog.add_text("<b>Phototag.ai API Key</b>")
    settings_dialog.add_input(
        settings_list.get_api_key(),
        var="phototag_api_key",
        width=input_width_large,
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        password=True,
    ).add_button("Update", callback=save_api_key_callback)
    settings_dialog.add_info(
        "An API key is required to access Phototag.ai services. Create an API key on the<br>"
        "<a href='https://phototag.ai'>Phototag.ai website</a>."
    )
    settings_dialog.add_text("Credits:").add_text("loading...", var="credits")
    settings_dialog.add_separator()

    # Keywords Section
    global keywords_section
    keywords_section = settings_dialog.start_section(
        "Keywords Settings",
        folded=local_settings.section_keywords_folded,
        var="keywords_section",
    )
    settings_dialog.add_text("Min Keywords:", width=label_width).add_input(
        str(current_settings.min_keywords or ""),
        var="min_keywords",
        width=input_width_small,
        placeholder="5-40",
    )
    settings_dialog.add_info("Minimum number of keywords to return (range: 5-40)")
    settings_dialog.add_text("Max Keywords:", width=label_width).add_input(
        str(current_settings.max_keywords or ""),
        var="max_keywords",
        width=input_width_small,
        placeholder="5-200",
    )
    settings_dialog.add_info(
        "Maximum number of keywords to return, overrides minKeywords (range: 5-200)"
    )
    settings_dialog.add_text("Required Keywords (comma-separated):")
    settings_dialog.add_input(
        current_settings.required_keywords or "",
        var="required_keywords",
        width=input_width_large,
        placeholder="e.g. portrait, studio, professional",
    )
    settings_dialog.add_info("Comma-separated keywords that must be included")
    settings_dialog.add_text("Excluded Keywords (comma-separated):")
    settings_dialog.add_input(
        current_settings.excluded_keywords or "",
        var="excluded_keywords",
        width=input_width_large,
        placeholder="e.g. landscape, nature, outdoor",
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
    global description_section
    description_section = settings_dialog.start_section(
        "Description Settings",
        folded=local_settings.section_description_folded,
        var="description_section",
    )
    settings_dialog.add_text(
        "Min Description Characters:", width=label_width
    ).add_input(
        str(current_settings.min_description_chars or ""),
        var="min_description_chars",
        width=input_width_small,
        placeholder="5-200",
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
        placeholder="50-500",
    )
    settings_dialog.add_info(
        "Maximum number of characters allowed in the description, overrides<br>minDescription (range: 50-500)"
    )
    settings_dialog.end_section()

    # Title Section
    global title_section
    title_section = settings_dialog.start_section(
        "Title Settings",
        folded=local_settings.section_title_folded,
        var="title_section",
    )
    settings_dialog.add_text("Min Title Characters:", width=label_width).add_input(
        str(current_settings.min_title_chars or ""),
        var="min_title_chars",
        width=input_width_small,
        placeholder="5-200",
    )
    settings_dialog.add_info(
        "Minimum number of characters allowed in the title (range: 5-200)"
    )
    settings_dialog.add_text("Max Title Characters:", width=label_width).add_input(
        str(current_settings.max_title_chars or ""),
        var="max_title_chars",
        width=input_width_small,
        placeholder="50-500",
    )
    settings_dialog.add_info(
        "Maximum number of characters allowed in the title, overrides minTitle<br>(range: 50-500)"
    )
    settings_dialog.add_checkbox(
        current_settings.title_case_title,
        var="title_case_title",
        text="Title Case Title",
    )
    settings_dialog.add_info("Use title case capitalization for the title")
    settings_dialog.end_section()

    # Additional Settings
    global additional_section
    additional_section = settings_dialog.start_section(
        "Additional Settings",
        folded=local_settings.section_additional_folded,
        var="additional_section",
    )
    settings_dialog.add_text("Custom Context:")
    settings_dialog.add_input(
        current_settings.custom_context or "",
        var="custom_context",
        width=input_width_large,
        placeholder="Additional context for AI generation",
    )
    settings_dialog.add_info("Additional context for keyword generation")
    settings_dialog.add_text("Prohibited Characters:")
    settings_dialog.add_input(
        current_settings.prohibited_characters or "",
        var="prohibited_characters",
        width=input_width_large,
        placeholder="!@#$%^&*()",
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
    global ai_attributes_section
    ai_attributes_section = settings_dialog.start_section(
        "AI Attributes",
        folded=local_settings.section_ai_attributes_folded,
        var="ai_attributes_section",
    )
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

    settings_dialog.add_separator()
    # Settings Management
    settings_dialog.add_text("<b>Settings Management</b>")
    names = settings_list.get_settings_names()
    settings_dialog.add_text("Settings Template").add_dropdown(
        current_settings.name,
        names,
        var="settings_name",
        width=200,
        callback=settings_dropdown_callback,
    )
    (
        settings_dialog.add_button("Save Settings", callback=save_settings_callback)
        .add_button(
            "New Settings",
            callback=lambda _: settings_dialog.hide_row("create_new_field", False),
            primary=False,
        )
        .add_button(
            "Rename",
            callback=lambda _: settings_dialog.hide_row("rename_field", False),
            primary=False,
        )
        .add_button(
            "Delete",
            callback=lambda _: settings_dialog.hide_row("delete_confirm", False),
            primary=False,
        )
    )
    (
        settings_dialog.add_info(
            "Settings can be saved as templates. If you trigger the action on a file, you will<br>be able to select the one of the defined settings templates."
        )
    )
    (
        settings_dialog.add_input("Default", var="create_new_field", width=200)
        .add_button(
            "Cancel",
            callback=lambda _: settings_dialog.hide_row("create_new_field", True),
            primary=False,
        )
        .add_button(
            "Create new Setting", callback=lambda _: confirm_create_new_settings()
        )
    )
    settings_dialog.hide_row("create_new_field", True)
    (
        settings_dialog.add_input(current_settings.name, var="rename_field", width=200)
        .add_button(
            "Cancel",
            callback=lambda _: settings_dialog.hide_row("rename_field", True),
            primary=False,
        )
        .add_button("Rename", callback=lambda _: confirm_rename_settings())
    )
    settings_dialog.hide_row("rename_field", True)
    (
        settings_dialog.add_text(
            f"Are you sure you want to delete the settings: {current_settings.name}?",
            var="delete_confirm",
        )
        .add_button("Yes", callback=lambda _: confirm_delete_settings(), primary=False)
        .add_button(
            "No",
            callback=lambda _: settings_dialog.hide_row("delete_confirm", True),
            primary=False,
        )
    )
    settings_dialog.hide_row("delete_confirm", True)

    # TODO: uncomment when get_folded() is implemented
    # settings_dialog.callback_closed = on_settings_dialog_closed

    settings_dialog.show()

    check_credits_callback(settings_dialog)


def on_settings_dialog_closed(dialog: ap.Dialog):
    """
    Callback for when the settings dialog is closed
    TODO: get_folded() doesn't exist
    """
    try:
        local_settings.last_edited = dialog.get_value("settings_name")

        local_settings.section_keywords_folded = keywords_section.get_folded()
        local_settings.section_description_folded = description_section.get_folded()
        local_settings.section_title_folded = title_section.get_folded()
        local_settings.section_additional_folded = additional_section.get_folded()
        local_settings.section_ai_attributes_folded = ai_attributes_section.get_folded()

        print(local_settings.section_keywords_folded)
        print(local_settings.section_description_folded)
        print(local_settings.section_title_folded)
        print(local_settings.section_additional_folded)
        print(local_settings.section_ai_attributes_folded)

    except Exception as e:
        print(e)

    local_settings.store()


def check_credits_callback(dialog: ap.Dialog):
    """
    Checks and displays the current credits balance
    """
    if not settings_list.get_api_key():
        return
    dialog.set_value("credits", "loading...")
    ctx = ap.get_context()
    ctx.run_async(check_credits, dialog)


def check_credits(dialog: ap.Dialog):
    """
    Checks and displays the current credits balance
    """
    response = get_phototag_credits()
    if response["error"]:
        ap.UI().show_error(f"Error checking credits: {response['error']}")
        return
    dialog.set_value("credits", str(response["data"]["credits"]))


def main():
    show_settings_dialog()


if __name__ == "__main__":
    main()
