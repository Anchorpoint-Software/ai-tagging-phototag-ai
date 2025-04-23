import os
import requests
from typing import Optional, Dict, Any
from phototag_settings import PhototagSettings
from phototag_settings_list import PhototagSettingsList

# Initialize settings list
settings_list = PhototagSettingsList()
API_URL = "https://server.phototag.ai/api/keywords"


def get_phototag_response(
    file_path: str, settings: PhototagSettings
) -> Optional[Dict[str, Any]]:
    """
    Sends an image file to the Phototag.ai API and returns the response.

    Args:
        file_path: Path to the image file to be analyzed
        settings: PhototagSettings instance containing API settings

    Returns:
        Dictionary containing the complete API response including data and error fields
    """
    if not settings_list.get_api_key():
        return {"error": "API Key Required", "data": None}

    headers = {"Authorization": f"Bearer {settings_list.get_api_key()}"}

    # Prepare API request payload with settings
    payload = {
        "keywordsOnly": False,
        "saveFile": False,
        "maxKeywords": settings.max_keywords,
        "minKeywords": settings.min_keywords,
        "requiredKeywords": settings.required_keywords,
        "excludedKeywords": settings.excluded_keywords,
        "customContext": settings.custom_context,
        "prohibitedCharacters": settings.prohibited_characters,
        "maxDescriptionCharacters": settings.max_description_chars,
        "minDescriptionCharacters": settings.min_description_chars,
        "maxTitleCharacters": settings.max_title_chars,
        "minTitleCharacters": settings.min_title_chars,
        "useFileNameForContext": settings.use_file_name_for_context,
        "singleWordKeywordsOnly": settings.single_word_keywords_only,
        "beCreative": settings.be_creative,
        "titleCaseTitle": settings.title_case_title,
    }

    # Remove None values from payload
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
            response = requests.post(
                API_URL, headers=headers, data=payload, files=files
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "data": None}
