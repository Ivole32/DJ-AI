"""
Prediction module for suggesting next tracks in DJ sets.

This module provides the inference API for the trained transition model.
Given a current track, it predicts the most likely next tracks based on
learned patterns from real DJ mixes.
"""

import pandas as pd
from pathlib import Path
from joblib import load
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TRACKS_CSV, MODEL_FILE
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))
from feature_builder import build_pair_features


class TrackPredictor:
    """
    Predictor for suggesting next tracks in a DJ set.
    
    Attributes:
        tracks (pd.DataFrame): Available tracks with their features
        model: Trained scikit-learn classifier
    """
    
    def __init__(self, tracks_path=None, model_path=None):
        """
        Initialize the predictor with tracks and model.
        
        Args:
            tracks_path (Path, optional): Path to tracks CSV. 
                                         Defaults to dataset/tracks.csv
            model_path (Path, optional): Path to trained model.
                                        Defaults to models/transition_model.joblib
        """
        # Set default paths from config
        if tracks_path is None:
            tracks_path = TRACKS_CSV
        if model_path is None:
            model_path = MODEL_FILE
        
        # Load tracks
        self.tracks = pd.read_csv(tracks_path)
        
        # Remove duplicates, keep last occurrence
        self.tracks = self.tracks.drop_duplicates(subset='youtube_id', keep='last')
        self.tracks = self.tracks.set_index("youtube_id")
        
        # Load model
        self.model = load(model_path)
    
    def suggest_next(self, track_id, top_k=10):
        """
        Suggest the best next tracks for a given track.
        
        Scores all candidate tracks and returns the top_k with highest
        predicted transition probability. Uses batch prediction for efficiency.
        
        Args:
            track_id (str): YouTube ID of the current track
            top_k (int): Number of suggestions to return. Default is 10.
            
        Returns:
            list: List of (track_id, score) tuples sorted by score (descending).
                  Score is the model's predicted probability of a good transition.
                  
        Raises:
            KeyError: If track_id is not found in the tracks dataset
        """
        if track_id not in self.tracks.index:
            raise KeyError(f"Track '{track_id}' not found in dataset")
        
        # Get all candidate tracks (exclude self)
        candidates = [c for c in self.tracks.index if c != track_id]
        
        # Build features for all candidates in batch
        features_list = []
        for candidate in candidates:
            feats = build_pair_features(self.tracks, track_id, candidate)
            features_list.append(feats)
        
        # Batch prediction (much faster than one-by-one)
        features_df = pd.DataFrame(features_list)
        probabilities = self.model.predict_proba(features_df)[:, 1]
        
        # Combine candidates with scores
        scores = list(zip(candidates, probabilities))
        
        # Return top_k results sorted by score
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]


# Global instance for backward compatibility
_predictor = None


def _get_predictor():
    """Get or create the global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = TrackPredictor()
    return _predictor


def suggest_next(track_id, top_k=10):
    """
    Suggest the best next tracks for a given track.
    
    This is a convenience function that uses a global predictor instance.
    For better control, create your own TrackPredictor instance.
    
    Args:
        track_id (str): YouTube ID of the current track
        top_k (int): Number of suggestions to return. Default is 10.
        
    Returns:
        list: List of (track_id, score) tuples sorted by score (descending)
    """
    predictor = _get_predictor()
    return predictor.suggest_next(track_id, top_k)