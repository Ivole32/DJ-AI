"""
Configuration for the audio analyzer.

Defines paths, performance settings, and audio processing parameters.
"""


# OS utilities
import os

# Multiprocessing for CPU count
from multiprocessing import cpu_count

# Path utilities
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
ANALYZER_DIR = PROJECT_ROOT / "analyzer"

# Files
JSON_FILE = DATASET_DIR / "dataset.json"

TMP_DIR = ANALYZER_DIR / "tmp"
OUT_DIR = DATASET_DIR

# Performance
DOWNLOAD_THREADS = 1
ANALYZE_PROCESSES = cpu_count()

# Audio cut
CUT_LENGTH = 60  # seconds

# Ensure directories exist
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True) 