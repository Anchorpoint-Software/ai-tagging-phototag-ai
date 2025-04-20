import os
import requests
from typing import Optional, Dict, Any
from phototag_settings import PhototagSettings

# Initialize settings and API endpoint
phototag_settings = PhototagSettings()
API_URL = "https://server.phototag.ai/api/keywords"

def get_phototag_response(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Sends an image file to the Phototag.ai API and returns the response.
    
    Args:
        file_path: Path to the image file to be analyzed
        
    Returns:
        Dictionary containing the complete API response including data and error fields
    """
    if not phototag_settings.phototag_api_key:
        return {"error": "API Key Required", "data": None}

    headers = {
        "Authorization": f"Bearer {phototag_settings.phototag_api_key}"
    }

    # Prepare API request payload with settings
    payload = {
        "keywordsOnly": False,
        "saveFile": False,
        "maxKeywords": phototag_settings.max_keywords,
        "minKeywords": phototag_settings.min_keywords,
        "requiredKeywords": phototag_settings.required_keywords,
        "excludedKeywords": phototag_settings.excluded_keywords,
        "customContext": phototag_settings.custom_context,
        "prohibitedCharacters": phototag_settings.prohibited_characters,
        "maxDescriptionCharacters": phototag_settings.max_description_chars,
        "minDescriptionCharacters": phototag_settings.min_description_chars,
        "maxTitleCharacters": phototag_settings.max_title_chars,
        "minTitleCharacters": phototag_settings.min_title_chars,
        "useFileNameForContext": phototag_settings.use_file_name_for_context,
        "singleWordKeywordsOnly": phototag_settings.single_word_keywords_only,
        "beCreative": phototag_settings.be_creative,
        "titleCaseTitle": phototag_settings.title_case_title
    }

    # Remove None values from payload
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'image/jpeg')
            }
            response = requests.post(API_URL, headers=headers, data=payload, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "data": None} 