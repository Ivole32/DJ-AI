"""
Configuration for the ML model.

Defines paths for training data, model files, and datasets.
"""

from pathlib import Path

# Project structure
ML_MODEL_DIR = Path(__file__).parent
PROJECT_ROOT = ML_MODEL_DIR.parent
DATASET_DIR = PROJECT_ROOT / "dataset"

# Input files
TRACKS_CSV = DATASET_DIR / "tracks.csv"
TRANSITIONS_CSV = DATASET_DIR / "transitions.csv"
DATASET_JSON = DATASET_DIR / "dataset.json"

# Model output
MODELS_DIR = ML_MODEL_DIR / "models"
MODEL_FILE = MODELS_DIR / "transition_model.joblib"

# Training hyperparameters
MAX_DEPTH = 6                # Tree depth (controls complexity)
MAX_ITER = 200               # Number of boosting iterations
LEARNING_RATE = 0.05         # Step size for gradient descent
MIN_SAMPLES_LEAF = 20        # Minimum samples per leaf node
L2_REGULARIZATION = 1.0      # L2 penalty for regularization
EARLY_STOPPING = True        # Stop if validation score doesn't improve
RANDOM_STATE = 42            # Reproducibility seed

# Training data generation
NEGATIVES_PER_POS = 3        # Number of negative examples per positive transition
MAX_FREQUENCY_WEIGHT = 3     # Cap on how many times to repeat frequent transitions

# Ensure model directory exists
MODELS_DIR.mkdir(parents=True, exist_ok=True)