"""
Feature engineering utilities for track pair analysis.

This module provides functions to build features from track pairs,
which are used for training the transition prediction model.
"""

import pandas as pd
import numpy as np


def camelot_distance(key_a, key_b):
    """
    Calculate the distance between two Camelot keys.
    
    The Camelot Wheel is a key notation system for harmonic mixing in DJing.
    Keys are represented as numbers (1-12) followed by a letter (A or B).
    
    Args:
        key_a (str): First Camelot key (e.g., "8A", "5B")
        key_b (str): Second Camelot key (e.g., "8A", "5B")
        
    Returns:
        int: Distance between keys
            - 0 if keys are identical
            - 1 if keys are adjacent on the wheel
            - 2 if keys have different modes (A vs B) but same number
            - Higher values for more distant keys
    """
    if key_a == key_b:
        return 0
    
    # Parse key components
    a_num, a_mode = int(key_a[:-1]), key_a[-1]
    b_num, b_mode = int(key_b[:-1]), key_b[-1]

    # Different modes (A vs B) have distance 2
    if a_mode != b_mode:
        return 2
    
    # Calculate circular distance on the wheel (1-12)
    return min(abs(a_num - b_num), 12 - abs(a_num - b_num))


def build_pair_features(tracks_df, track_a_id, track_b_id):
    """
    Build feature vector for a pair of tracks.
    
    Extracts relevant features from two tracks to predict if they would
    make a good transition in a DJ mix.
    
    Args:
        tracks_df (pd.DataFrame): DataFrame containing track information,
                                  indexed by track ID
        track_a_id (str): ID of the first track (source)
        track_b_id (str): ID of the second track (destination)
        
    Returns:
        dict: Dictionary of features:
            - bpm_diff: Absolute BPM difference between tracks
            - bpm_ratio: BPM ratio (for tempo shifts)
            - energy_diff: Change in energy (positive = energy increase)
            - energy_product: Product of energies (both high/low energy)
            - key_dist: Camelot key distance
            - same_key: Binary flag (1 if same key, 0 otherwise)
            - tempo_match: Binary flag (1 if BPM difference <= 2, 0 otherwise)
            - tempo_match_loose: Binary flag (1 if BPM difference <= 5, 0 otherwise)
            - energy_boost: Binary flag (1 if energy increases significantly)
            - energy_drop: Binary flag (1 if energy drops significantly)
    """
    track_a = tracks_df.loc[track_a_id]
    track_b = tracks_df.loc[track_b_id]
    
    bpm_diff = abs(track_a['bpm'] - track_b['bpm'])
    energy_diff = track_b['energy'] - track_a['energy']
    
    return {
        # BPM features
        "bpm_diff": bpm_diff,
        "bpm_ratio": track_b['bpm'] / track_a['bpm'] if track_a['bpm'] > 0 else 1.0,
        
        # Energy features
        "energy_diff": energy_diff,
        "energy_product": track_a['energy'] * track_b['energy'],
        
        # Key features
        "key_dist": camelot_distance(track_a['camelot'], track_b['camelot']),
        "same_key": int(track_a['camelot'] == track_b['camelot']),
        
        # Binary tempo matches
        "tempo_match": int(bpm_diff <= 2),
        "tempo_match_loose": int(bpm_diff <= 5),
        
        # Energy dynamics
        "energy_boost": int(energy_diff > 0.1),
        "energy_drop": int(energy_diff < -0.1),
    }