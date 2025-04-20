import os
import requests
from typing import Optional, Dict, Any

import anchorpoint as ap
import apsync as aps
from phototag_settings import PhototagSettings
from phototag_api import get_phototag_response

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
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.tiff'}
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
    progress = ap.Progress("Tagging Files", "Processing", infinite=False, show_loading_screen=True, cancelable=True)
    
    for i, file_path in enumerate(file_paths):
        # Check if user canceled the operation
        if progress.canceled:
            progress.finish()
            return
            
        progress.report_progress(i / len(file_paths))
        
        result = get_phototag_response(file_path)
        if result.get("error"):
            ap.UI().show_error("API Error", result["error"])
            continue

        data = result.get("data")
        if not data:
            continue

        # Update file attributes with AI-generated content
        if data.get("title") and phototag_settings.enable_ai_title:
            database.attributes.set_attribute_value(file_path, "AI-Title", data["title"])
        
        if data.get("description") and phototag_settings.enable_ai_description:
            database.attributes.set_attribute_value(file_path, "AI-Description", data["description"])
        
        if data.get("keywords") and phototag_settings.enable_ai_tags:
            keywords = aps.AttributeTagList()
            for keyword in data["keywords"]:
                keywords.append(aps.AttributeTag(keyword))
            database.attributes.set_attribute_value(file_path, "AI-Keywords", keywords)

    progress.finish()
    ap.UI().show_success("Tagging Complete", f"Processed {len(file_paths)} files")

def main():
    """
    Main entry point that handles file selection and starts the tagging process.
    Supports both individual files and entire folders.
    """
    ctx = ap.get_context()
    if not ctx.selected_files and not ctx.selected_folders:
        ap.UI().show_error("No Files Selected", "Please select image files or folders to tag")
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

if __name__ == "__main__":
    main() 