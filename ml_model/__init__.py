"""
DJ-AI Machine Learning Model Package.

This package provides machine learning capabilities for predicting
optimal track transitions in DJ sets.

Modules:
    - data_preparation: Extract and preprocess training data
    - training: Train the transition prediction model
    - inference: Make predictions for next tracks
    - utils: Shared utilities and feature engineering
"""

__version__ = "1.0.0"

# Import main prediction function for convenience
from .inference.predict import suggest_next, TrackPredictor
from .inference.validation import validate_model_files, validate_imports, quick_validate

__all__ = ['suggest_next', 'TrackPredictor', 'validate_model_files', 'validate_imports', 'quick_validate']