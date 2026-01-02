"""
Utility function to load dataset from a JSON file.
"""

# Import dataset path from config
from api.config.config import DATASET_PATH

# Import JSON handling library
import orjson

def load_dataset() -> list:
    """
    Load JSON dataset from the specified path.

    Returns:
        list: List of mixes with tracklists
    """
    with open(DATASET_PATH, "rb") as f:
        return orjson.loads(f.read())