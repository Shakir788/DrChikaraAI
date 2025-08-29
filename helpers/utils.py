import base64
import re
from langdetect import detect

def process_image(file):
    """Process uploaded image and return base64 encoded string."""
    bytes_data = file.getvalue()
    mime = "image/png" if file.name.lower().endswith(".png") else "image/jpeg"
    return base64.b64encode(bytes_data).decode("utf-8"), mime

def detect_mood(text):
    """Detect mood based on input text."""
    if "sad" in text.lower() or "tired" in text.lower() or "stress" in text.lower():
        return "sad"
    elif "happy" in text.lower() or "great" in text.lower() or "excited" in text.lower():
        return "happy"
    return "neutral"

def remove_emojis(text):
    """Remove emojis from text."""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002500-\U00002BEF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)

def js_escape(s):
    """Escape Python string for safe embedding in JS."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")