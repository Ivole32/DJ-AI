"""
Training data generation for the transition prediction model.

This module builds labeled training sets from real DJ transitions (positive examples)
and random track pairs (negative examples).
"""

import random
import pandas as pd
import sys
from pathlib import Path

# Add parent and utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MAX_FREQUENCY_WEIGHT
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))
from feature_builder import build_pair_features


def build_training_set(tracks, transitions_df, negatives_per_pos=3):
    """
    Build training set from transitions DataFrame.
    
    Creates a balanced dataset by:
    1. Using real DJ transitions as positive examples
    2. Generating random track pairs as negative examples
    3. Weighting positive examples by their frequency (capped at 3)
    
    Args:
        tracks (pd.DataFrame): DataFrame with track features indexed by track_id.
                               Required columns: bpm, energy, camelot
        transitions_df (pd.DataFrame): DataFrame with columns:
                                       [from_track_id, to_track_id, frequency]
        negatives_per_pos (int): Number of negative examples per positive transition.
                                 Default is 3 for balanced classes.
    
    Returns:
        tuple: (X, y) where:
            - X (pd.DataFrame): Feature matrix with columns from build_pair_features
            - y (list): Binary labels (1 for real transitions, 0 for negatives)
    """
    X, y = [], []

    # Iterate through transitions, considering frequency
    for _, row in transitions_df.iterrows():
        from_id = row['from_track_id']
        to_id = row['to_track_id']
        freq = row['frequency']
        
        # Skip if tracks not in dataset
        if from_id not in tracks.index or to_id not in tracks.index:
            continue
        
        # Add positive examples (weighted by frequency)
        # Use frequency to determine how many times to include this transition
        # Cap to avoid over-weighting popular transitions
        for _ in range(min(freq, MAX_FREQUENCY_WEIGHT)):
            X.append(build_pair_features(tracks, from_id, to_id))
            y.append(1)

        # Add negative examples (random pairs that are likely bad transitions)
        candidates = tracks.index.difference([from_id, to_id])
        for _ in range(negatives_per_pos):
            neg = random.choice(candidates)
            X.append(build_pair_features(tracks, from_id, neg))
            y.append(0)

    return pd.DataFrame(X), y