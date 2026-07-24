# config.py

GEMINI_API_KEY = "AQ.Ab8RN6I1Xj0wOrO0kGAvO7XiptvCzQyHPXLZxSCOoYUMyQjhzg"
MODEL_NAME = "gemini-3.6-flash"

def is_api_key_configured():
    # Simply checks if a key exists and is longer than a few characters
    return len(GEMINI_API_KEY.strip()) > 20