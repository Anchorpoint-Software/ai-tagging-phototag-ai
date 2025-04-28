import os
import requests
from typing import Optional, Dict, Any
import tempfile
import anchorpoint as ap
import apsync as aps
from phototag_settings import PhototagSettings
from phototag_api import get_phototag_response
from phototag_settings_list import PhototagSettingsList
from phototag_local_settings import PhototagLocalSettings
from supported_extensions import SUPPORTED_EXTENSIONS

# Initialize settings
phototag_settings = PhototagSettings()
local_settings = PhototagLocalSettings()


def get_all_files_recursive(folder_path) -> list[str]:
    """
    Recursively collects all supported files from a folder and its subfolders.
    Only includes extensions in SUPPORTED_EXTENSIONS.

    Args:
        folder_path: Path to the root folder to scan

    Returns:
        List of absolute file paths
    """
    files = []
    for root, _, file_names in os.walk(folder_path):
        for file_name in file_names:
            if os.path.splitext(file_name)[1].lower() in SUPPORTED_EXTENSIONS:
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
    
    temp_dir = os.path.join(tempfile.gettempdir(), "anchorpoint", "phototag_ai", "previews")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for i, file_path in enumerate(file_paths):
        # Check if user canceled the operation
        if progress.canceled:
            progress.finish()
            return

        progress.report_progress(i / len(file_paths))
        
        thumbnail_path = aps.get_thumbnail(file_path, False)
        if not thumbnail_path:
            success = aps.generate_thumbnail(file_path, temp_dir, with_detail=True, with_preview=True)
            if not success:
                ap.UI().show_error("Failed to generate thumbnail", f"Failed to generate thumbnail for {file_path}")
                continue
            # file_name_pt.png
            file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]
            thumbnail_path = os.path.join(temp_dir, file_name_without_ext + "_dt.png")

        result = get_phototag_response(thumbnail_path, phototag_settings)
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


def select_settings_callback(dialog: ap.Dialog, selected_files):
    """
    Callback for selecting Phototag settings.
    """
    name = dialog.get_value("settings_name")
    settings = PhototagSettingsList()
    global phototag_settings
    phototag_settings = settings.get_setting(name)
    if phototag_settings:
        local_settings.last_selected = phototag_settings.name
        local_settings.store()
        dialog.close()
        process_selected_files(selected_files)
    else:
        ap.UI().show_error("Failed to load settings")


def show_settings_selection(selected_files):
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
        process_selected_files(selected_files)
        return True

    if len(names) == 1:
        # Use the only saved settings, don't show the dialog
        phototag_settings = settings.get_setting(names[0])
        process_selected_files(selected_files)
        return True

    ctx = ap.get_context()
    dialog = ap.Dialog()
    dialog.closable = False
    dialog.title = "Select Phototag Settings"
    dialog.icon = ctx.icon
    default_name = local_settings.last_selected if local_settings.last_selected in names else names[0]
    dialog.add_text("Select Settings:").add_dropdown(
        default_name, names, var="settings_name"
    )
    (
        dialog.add_button("Tag", callback=lambda d: select_settings_callback(d, selected_files))
        .add_button(
            "Cancel", primary=False, callback=lambda _: dialog.close()
        )
    )
    dialog.show()
    return True


def process_selected_files(selected_files):
    """
    Processes the selected files or folders by sending them to Phototag.ai and updating their attributes.
    """
    if not selected_files:
        ap.UI().show_error("No Files Found", "No files found in selected files or folders")
        return

    # Start async processing
    database = ap.get_api()
    ctx = ap.get_context()
    ctx.run_async(process_files, selected_files, database)


def main():
    ctx = ap.get_context()
    if not ctx.selected_files and not ctx.selected_folders:
        ap.UI().show_error(
            "No Files Selected", "Please select image files or folders to tag"
        )
        return

    # Prepare selected_files first
    selected_files = [
        f for f in ctx.selected_files
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    ]
    for folder in ctx.selected_folders:
        selected_files.extend(get_all_files_recursive(folder))
        
    if not selected_files:
        ap.UI().show_error("No Supported Files Found", "No supported files found in selected files or folders")
        return

    show_settings_selection(selected_files)


if __name__ == "__main__":
    main()
