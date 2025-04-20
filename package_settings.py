import anchorpoint as ap
import apsync as aps
import os
from typing import Optional
from phototag_settings import PhototagSettings

phototag_settings = PhototagSettings()

def delete_api_key_callback(dialog: ap.Dialog):
    phototag_settings.phototag_api_key = ""
    dialog.set_value("phototag_api_key", "")
    phototag_settings.store()

def validate_int_range(value: str, min_val: int, max_val: int) -> bool:
    try:
        num = int(value)
        return min_val <= num <= max_val
    except ValueError:
        return False

def apply_callback(dialog: ap.Dialog):
    # Store API key
    phototag_settings.phototag_api_key = str(dialog.get_value("phototag_api_key"))

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
    phototag_settings.max_keywords = int(max_keywords) if max_keywords else 0
    phototag_settings.min_keywords = int(min_keywords) if min_keywords else 0
    phototag_settings.required_keywords = str(dialog.get_value("required_keywords") or "")
    phototag_settings.excluded_keywords = str(dialog.get_value("excluded_keywords") or "")
    phototag_settings.custom_context = str(dialog.get_value("custom_context") or "")
    phototag_settings.prohibited_characters = str(dialog.get_value("prohibited_characters") or "")
    phototag_settings.max_description_chars = int(max_desc) if max_desc else 0
    phototag_settings.min_description_chars = int(min_desc) if min_desc else 0
    phototag_settings.max_title_chars = int(max_title) if max_title else 0
    phototag_settings.min_title_chars = int(min_title) if min_title else 0
    phototag_settings.use_file_name_for_context = bool(dialog.get_value("use_file_name_for_context"))
    phototag_settings.single_word_keywords_only = bool(dialog.get_value("single_word_keywords_only"))
    phototag_settings.be_creative = bool(dialog.get_value("be_creative"))
    phototag_settings.title_case_title = bool(dialog.get_value("title_case_title"))
    
    phototag_settings.enable_ai_title = bool(dialog.get_value("enable_ai_title"))
    phototag_settings.enable_ai_description = bool(dialog.get_value("enable_ai_description"))
    phototag_settings.enable_ai_tags = bool(dialog.get_value("enable_ai_tags"))

    phototag_settings.store()
    ap.UI().show_success("Settings Updated")
    dialog.close()

def main():
    
    label_width = 292
    input_width_small = 100
    input_width_large = 400
    
    dialog = ap.Dialog()
    dialog.title = "Phototag.ai Settings"
    ctx = ap.get_context()
    if ctx.icon:
        dialog.icon = ctx.icon

    # API Key Section
    dialog.add_text("<b>Phototag.ai API Key</b>")
    dialog.add_input(
        phototag_settings.phototag_api_key, 
        var="phototag_api_key", 
        width=input_width_large, 
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
        password=True
    ).add_button("Delete", callback=delete_api_key_callback)
    dialog.add_info(
        "An API key is required to access Phototag.ai services. Create an API key on "
        "<a href='https://phototag.ai'>the Phototag.ai website</a>."
    )
    dialog.add_separator()
    


    # Keywords Section
    dialog.start_section("Keywords Settings", folded=False)
    dialog.add_text("Min Keywords:", width=label_width).add_input(str(phototag_settings.min_keywords or ""), var="min_keywords", width=input_width_small)
    dialog.add_info("Minimum number of keywords to return (range: 5-40)")
    dialog.add_text("Max Keywords:", width=label_width).add_input(str(phototag_settings.max_keywords or ""), var="max_keywords", width=input_width_small)
    dialog.add_info("Maximum number of keywords to return, overrides minKeywords (range: 5-200)")
    dialog.add_text("Required Keywords (comma-separated):")
    dialog.add_input(phototag_settings.required_keywords or "", var="required_keywords", width=input_width_large)
    dialog.add_info("Comma-separated keywords that must be included")
    dialog.add_text("Excluded Keywords (comma-separated):")
    dialog.add_input(phototag_settings.excluded_keywords or "", var="excluded_keywords", width=input_width_large)
    dialog.add_info("Comma-separated keywords that must be excluded")
    dialog.add_checkbox(phototag_settings.single_word_keywords_only, var="single_word_keywords_only", text="Single Word Keywords Only")
    dialog.add_info("Only allow single-word keywords")
    dialog.end_section()

    # Description Section
    dialog.start_section("Description Settings", folded=False)
    dialog.add_text("Min Description Characters:", width=label_width).add_input(str(phototag_settings.min_description_chars or ""), var="min_description_chars", width=input_width_small)
    dialog.add_info("Minimum number of characters allowed in the description (range: 5-200)")
    dialog.add_text("Max Description Characters:", width=label_width).add_input(str(phototag_settings.max_description_chars or ""), var="max_description_chars", width=input_width_small)
    dialog.add_info("Maximum number of characters allowed in the description, overrides minDescription (range: 50-500)")
    dialog.end_section()

    # Title Section
    dialog.start_section("Title Settings", folded=False)
    dialog.add_text("Min Title Characters:", width=label_width).add_input(str(phototag_settings.min_title_chars or ""), var="min_title_chars", width=input_width_small)
    dialog.add_info("Minimum number of characters allowed in the title (range: 5-200)")
    dialog.add_text("Max Title Characters:", width=label_width).add_input(str(phototag_settings.max_title_chars or ""), var="max_title_chars", width=input_width_small)
    dialog.add_info("Maximum number of characters allowed in the title, overrides minTitle (range: 50-500)")
    dialog.add_checkbox(phototag_settings.title_case_title, var="title_case_title", text="Title Case Title")
    dialog.add_info("Use title case capitalization for the title")
    dialog.end_section()

    # Additional Settings
    dialog.start_section("Additional Settings", folded=False)
    dialog.add_text("Custom Context:")
    dialog.add_input(phototag_settings.custom_context or "", var="custom_context", width=input_width_large)
    dialog.add_info("Additional context for keyword generation")
    dialog.add_text("Prohibited Characters:")
    dialog.add_input(phototag_settings.prohibited_characters or "", var="prohibited_characters", width=input_width_large)
    dialog.add_info("Characters to be removed from the title, description, and keywords")
    dialog.add_checkbox(phototag_settings.use_file_name_for_context, var="use_file_name_for_context", text="Use File Name for Context")
    dialog.add_info("Use the file name as context for keyword generation")
    dialog.add_checkbox(phototag_settings.be_creative, var="be_creative", text="Be Creative")
    dialog.add_info("Make the title and description more creative and artistic")
    dialog.end_section()

    # AI Attributes Section
    dialog.start_section("AI Attributes", folded=False)
    dialog.add_checkbox(phototag_settings.enable_ai_title, var="enable_ai_title", text="Enable AI-Title")
    dialog.add_info("Generate and apply AI-generated titles")
    dialog.add_checkbox(phototag_settings.enable_ai_description, var="enable_ai_description", text="Enable AI-Description")
    dialog.add_info("Generate and apply AI-generated descriptions")
    dialog.add_checkbox(phototag_settings.enable_ai_tags, var="enable_ai_tags", text="Enable AI-Tags")
    dialog.add_info("Generate and apply AI-generated tags")
    dialog.end_section()

    dialog.add_button("Apply", callback=apply_callback)
    dialog.show()

if __name__ == "__main__":
    main() 