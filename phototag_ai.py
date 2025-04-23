import os
import requests
from typing import Optional, Dict, Any

import anchorpoint as ap
import apsync as aps
from phototag_settings import PhototagSettings
from phototag_api import get_phototag_response
from phototag_settings_list import PhototagSettingsList

# Initialize settings
phototag_settings = PhototagSettings()


def get_all_files_recursive(folder_path) -> list[str]:
    """
    Recursively collects all image files from a folder and its subfolders.
    Only includes: png, jpg, jpeg, webp, svg, tiff formats.

    Args:
        folder_path: Path to the root folder to scan

    Returns:
        List of absolute file paths
    """
    files = []
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".tiff"}
    for root, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            if os.path.splitext(file_name)[1].lower() in image_extensions:
                files.append(str(os.path.join(root, file_name)))
    return files


def process_files(file_paths, database):
    """
    Processes a list of files by sending them to Phototag.ai and updating their attributes.

    Args:
        file_paths: List of file paths to process
        database: Anchorpoint database instance for attribute updates
    """
    # Create a progress dialog that can be canceled
    progress = ap.Progress(
        "Tagging Files",
        "Processing",
        infinite=False,
        show_loading_screen=True,
        cancelable=True,
    )

    for i, file_path in enumerate(file_paths):
        # Check if user canceled the operation
        if progress.canceled:
            progress.finish()
            return

        progress.report_progress(i / len(file_paths))

        result = get_phototag_response(file_path, phototag_settings)
        if result.get("error"):
            ap.UI().show_error("API Error", result["error"])
            continue

        data = result.get("data")
        if not data:
            continue

        # Update file attributes with AI-generated content
        if data.get("title") and phototag_settings.enable_ai_title:
            database.attributes.set_attribute_value(
                file_path, "AI-Title", data["title"]
            )

        if data.get("description") and phototag_settings.enable_ai_description:
            database.attributes.set_attribute_value(
                file_path, "AI-Description", data["description"]
            )

        if data.get("keywords") and phototag_settings.enable_ai_tags:
            keywords = aps.AttributeTagList()
            for keyword in data["keywords"]:
                keywords.append(aps.AttributeTag(keyword))
            database.attributes.set_attribute_value(file_path, "AI-Keywords", keywords)

    progress.finish()
    ap.UI().show_success("Tagging Complete", f"Processed {len(file_paths)} files")


def select_settings_callback(dialog: ap.Dialog):
    """
    Callback for selecting Phototag settings.
    """
    name = dialog.get_value("settings_name")
    settings = PhototagSettingsList()
    global phototag_settings
    phototag_settings = settings.get_setting(name)
    if phototag_settings:
        dialog.close()
        process_selected_files()
    else:
        ap.UI().show_error("Failed to load settings")


def show_settings_selection():
    """
    Displays a dialog to select Phototag settings.
    If no settings are saved, it uses the default settings without showing the dialog.
    If there is only one saved setting, it uses that setting without showing the dialog.
    If there are multiple settings, it shows the dialog to select one.
    """
    settings = PhototagSettingsList()
    names = settings.get_settings_names()
    if not names:
        ap.UI().show_error("No saved settings found")
        return False
    global phototag_settings
    if len(names) == 0:
        # Use default settings
        phototag_settings = PhototagSettings()
        return True

    if len(names) == 1:
        # Use the only saved settings, don't show the dialog
        phototag_settings = settings.get_setting(names[0])
        return True

    dialog = ap.Dialog()
    dialog.closable = False
    dialog.title = "Select Phototag Settings"
    dialog.add_text("Select Settings:").add_dropdown(
        names[0], names, var="settings_name"
    )
    (
        dialog.add_button(
            "Cancel", primary=False, callback=lambda _: dialog.close()
        ).add_button("Tag", callback=select_settings_callback)
    )
    dialog.show()
    return True


def process_selected_files():
    """
    Processes the selected files or folders by sending them to Phototag.ai and updating their attributes.
    """
    ctx = ap.get_context()
    if not ctx.selected_files and not ctx.selected_folders:
        ap.UI().show_error(
            "No Files Selected", "Please select image files or folders to tag"
        )
        return

    # Collect all files to process
    selected_files = ctx.selected_files.copy()

    # Add files from selected folders
    for folder in ctx.selected_folders:
        selected_files.extend(get_all_files_recursive(folder))

    if not selected_files:
        ap.UI().show_error("No Files Found", "No files found in selected folders")
        return

    # Start async processing
    database = ap.get_api()
    ctx.run_async(process_files, selected_files, database)


def main():
    show_settings_selection()


if __name__ == "__main__":
    main()
