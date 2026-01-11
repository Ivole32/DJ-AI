"""
Track Metadata Utility
Loads track metadata from dataset.json and tracks.csv
"""

import json
import csv
import os
from functools import lru_cache
from typing import Optional, Dict

# Cache the dataset for performance
_dataset_cache = None
_tracks_cache = None

def _load_dataset() -> Dict[str, Dict]:
    """Load dataset.json and create a lookup dict by youtube_id"""
    global _dataset_cache
    if _dataset_cache is not None:
        return _dataset_cache
    
    dataset_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'dataset.json')
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create lookup dict: youtube_id -> track info
        lookup = {}
        for mix in data:
            for track in mix.get('tracklist', []):
                youtube_id = track.get('id')
                title = track.get('title', '')
                if youtube_id:
                    # Parse title to extract artist and track name
                    # Format is usually "[XX] Artist - Track Name"
                    parts = title.split('] ', 1)
                    if len(parts) == 2:
                        track_info = parts[1]
                        if ' - ' in track_info:
                            artist, track_name = track_info.split(' - ', 1)
                        else:
                            artist = 'Unknown Artist'
                            track_name = track_info
                    else:
                        artist = 'Unknown Artist'
                        track_name = title
                    
                    lookup[youtube_id] = {
                        'title': track_name.strip(),
                        'artist': artist.strip(),
                        'full_title': title
                    }
        
        _dataset_cache = lookup
        return lookup
    except Exception as e:
        from api.logger.logger import logger
        logger.error(f"Error loading dataset.json: {e}")
        return {}

def _load_tracks_csv() -> Dict[str, Dict]:
    """Load tracks.csv and create a lookup dict by youtube_id"""
    global _tracks_cache
    if _tracks_cache is not None:
        return _tracks_cache
    
    tracks_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'tracks.csv')
    
    try:
        lookup = {}
        with open(tracks_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                youtube_id = row.get('youtube_id')
                if youtube_id:
                    lookup[youtube_id] = {
                        'bpm': float(row['bpm']) if row.get('bpm') else None,
                        'key': row.get('key'),
                        'camelot': row.get('camelot'),
                        'energy': float(row['energy']) if row.get('energy') else None
                    }
        
        _tracks_cache = lookup
        return lookup
    except Exception as e:
        from api.logger.logger import logger
        logger.error(f"Error loading tracks.csv: {e}")
        return {}

@lru_cache(maxsize=10000)
def get_track_metadata(youtube_id: str) -> Optional[Dict]:
    """
    Get complete track metadata for a given youtube_id
    
    Args:
        youtube_id: The YouTube video ID
        
    Returns:
        Dict with keys: title, artist, bpm, key, camelot, energy (None if not found)
    """
    dataset = _load_dataset()
    tracks = _load_tracks_csv()
    
    # Combine data from both sources
    metadata = {
        'title': None,
        'artist': None,
        'bpm': None,
        'key': None,
        'camelot': None,
        'energy': None
    }
    
    # Get title and artist from dataset.json
    if youtube_id in dataset:
        metadata['title'] = dataset[youtube_id]['title']
        metadata['artist'] = dataset[youtube_id]['artist']
    
    # Get technical data from tracks.csv
    if youtube_id in tracks:
        metadata['bpm'] = tracks[youtube_id]['bpm']
        metadata['key'] = tracks[youtube_id]['key']
        metadata['camelot'] = tracks[youtube_id]['camelot']
        metadata['energy'] = tracks[youtube_id]['energy']
    
    return metadata

def reload_cache():
    """Reload the dataset cache (useful for testing or updates)"""
    global _dataset_cache, _tracks_cache
    _dataset_cache = None
    _tracks_cache = None
    get_track_metadata.cache_clear()
