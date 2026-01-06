"""
Train the transition prediction model.

This script:
1. Loads track features and transition data
2. Builds a training set with positive and negative examples
3. Trains a HistGradientBoostingClassifier
4. Saves the trained model to disk
"""

import pandas as pd
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier
from joblib import dump
import sys

# Fix imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    TRACKS_CSV, TRANSITIONS_CSV, MODEL_FILE,
    MAX_DEPTH, MAX_ITER, LEARNING_RATE, MIN_SAMPLES_LEAF,
    L2_REGULARIZATION, EARLY_STOPPING, RANDOM_STATE, NEGATIVES_PER_POS
)
sys.path.insert(0, str(Path(__file__).parent))
from training_data import build_training_set


def main():
    """
    Main training pipeline.
    
    Loads data, trains model, and saves it for inference.
    """
    # Use paths from centralized config
    tracks_path = TRACKS_CSV
    transitions_path = TRANSITIONS_CSV
    model_output_path = MODEL_FILE

    # Load track features
    print(f"Loading tracks from: {tracks_path}")
    tracks = pd.read_csv(tracks_path)

    # Remove duplicates, keep last occurrence (most recent analysis)
    tracks = tracks.drop_duplicates(subset='youtube_id', keep='last')
    tracks = tracks.set_index("youtube_id")
    print(f"Loaded {len(tracks)} unique tracks")

    # Load transitions
    print(f"Loading transitions from: {transitions_path}")
    transitions_df = pd.read_csv(transitions_path)
    print(f"Loaded {len(transitions_df)} unique transitions")

    # Build training set
    print("Building training set...")
    X, y = build_training_set(tracks, transitions_df, negatives_per_pos=NEGATIVES_PER_POS)
    print(f"Training set size: {len(X)} examples ({sum(y)} positive, {len(y) - sum(y)} negative)")

    # Train model
    print("Training model...")
    model = HistGradientBoostingClassifier(
        max_depth=MAX_DEPTH,
        max_iter=MAX_ITER,
        learning_rate=LEARNING_RATE,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        l2_regularization=L2_REGULARIZATION,
        early_stopping=EARLY_STOPPING,
        random_state=RANDOM_STATE
    )
    
    model.fit(X, y)

    # Save model
    print(f"Saving model to: {model_output_path}")
    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, model_output_path)
    
    print("Training complete!")
    print(f"Model saved successfully")


if __name__ == '__main__':
    main()