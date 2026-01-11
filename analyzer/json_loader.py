"""Dataset loader utilities.

Provides functions to extract YouTube video IDs from the dataset.
"""


# JSON for dataset loading
import json

# Config for dataset path
from config import JSON_FILE

def load_youtube_ids():
    """Load all unique YouTube video IDs from the dataset.
    
    Extracts IDs from all tracks in all mixes in the dataset JSON file.
    
    Returns:
        list: List of unique YouTube video IDs
    """
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    ids = set()

    for mix in data:
        for track in mix.get("tracklist", []):
            vid = track.get("id")
            if vid:
                ids.add(vid)

    return list(ids)