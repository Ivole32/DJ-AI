"""
Fuzzy search utility for track identification.
Uses RapidFuzz for efficient fuzzy matching.
"""


# Fuzzy searching libraries
from rapidfuzz import process, fuzz

# Caching
from api.cache.redis_handler import RedisHandler

# Dataset loader
from api.utils.load_dataset import load_dataset

# Config for tracks CSV path
from api.config.config import TRACKS_CSV_PATH

# Track metadata utility
from api.utils.track_metadata import get_track_metadata

# CSV handling
import csv

# Initialize Redis cache handler
cache = RedisHandler(host = "redis", default_ttl=600)


class TrackSearcher:
    """Fuzzy search service for track identification using RapidFuzz.
    
    Performance Optimizations:
    - Pre-builds searchable candidates on initialization (format: 'id title')
    - Uses Redis caching with 600s TTL to avoid repeated fuzzy matching
    - Cache key includes query + parameters for precise hit detection
    - RapidFuzz's token_sort_ratio handles word order variations
    - Only returns tracks that exist in tracks.csv
    
    Search Strategy:
    - Concatenates track ID and title for better matching ('abc123 Track Name')
    - Allows searching by ID (exact) or title (fuzzy)
    - Returns top N matches with similarity scores
    - Can filter out tracks without IDs (return_null_ids parameter)
    - Filters results to only include tracks present in tracks.csv
    
    Attributes:
        data (list): Raw dataset loaded from dataset.json
        tracks (list): Pre-processed candidate dictionaries for search
        valid_track_ids (set): Set of YouTube IDs from tracks.csv
    """

    def __init__(self):
        # Initialize dataset and valid track IDs
        self.data = load_dataset()
        self.valid_track_ids = self._load_valid_track_ids()
        self.tracks = self._build_candidates()
    
    def _load_valid_track_ids(self) -> set:
        """
        Load valid YouTube track IDs from tracks.csv.

        Returns:
            set: Set of valid YouTube IDs
        """
        valid_ids = set()
        try:
            with open(TRACKS_CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    youtube_id = row.get('youtube_id')
                    if youtube_id:
                        valid_ids.add(youtube_id)
        except Exception as e:
            from api.logger.logger import logger
            logger.warning(f"Could not load tracks.csv: {e}")
        return valid_ids

    def _build_candidates(self) -> list:
        tracks = []
        seen_ids = set()

        for mix in self.data:
            for track in mix.get("tracklist", []):
                track_id = track.get("id")

                if (
                    not track_id
                    or track_id not in self.valid_track_ids
                    or track_id in seen_ids
                ):
                    continue

                seen_ids.add(track_id)

                title = track.get("title") or ""

                tracks.append({
                    "candidate": f"{track_id} {title}",
                    "id": track_id,
                    "title": title,
                })

        return tracks
    
    def search_track(self, query, top=5, return_null_ids=False) -> list[dict]:
        """
        Perform a fuzzy search for tracks by ID or title.

        Args:
            query (str): Track ID or title (may be misspelled).
            top (int): Number of top results to return.
            return_null_ids (bool): Whether tracks without IDs should be included.

        Returns:
            list[dict]: List of top matching tracks, each with its score.
        """
        cache_key = cache.make_key(
            "track_search",
            query,
            top,
            return_null_ids
        )

        cached = cache.get(cache_key)
        if cached:
            return cached

        # Filter tracks based on ID presence
        filtered_tracks = [
            t for t in self.tracks
            if return_null_ids or t.get("id") is not None
        ]

        # Canidate strings for fuzzy matching
        candidates = [t["candidate"] for t in filtered_tracks]

        results = process.extract(
            query,
            candidates,
            scorer=fuzz.token_sort_ratio,
            limit=top
        )

        matches = []
        for _, score, idx in results:
            track_info = filtered_tracks[idx].copy()
            track_info["score"] = score
            
            # Add metadata from tracks.csv
            track_id = track_info.get('id')
            if track_id:
                metadata = get_track_metadata(track_id)
                if metadata:
                    track_info['artist'] = metadata.get('artist')
                    track_info['bpm'] = metadata.get('bpm')
                    track_info['key'] = metadata.get('key')
                    track_info['camelot'] = metadata.get('camelot')
                    track_info['energy'] = metadata.get('energy')
            
            matches.append(track_info)
        
        cache.set(cache_key, matches, ttl=600)
        return matches
    
    def is_ready(self) -> bool:
        """
        Check if the searcher is ready (dataset loaded).

        Returns:
            bool: True if dataset is loaded, False otherwise.
        """
        return bool(self.data and self.tracks) # Check if data and tracks are loaded


# Test code
if __name__ == "__main__":
    searcher = TrackSearcher() # Initialize searcher instance

    query = "[00] Jhalib - Mysteries Of The world"
    results = searcher.search_track(query, top=5)
    from api.logger.logger import logger
    for r in results:
        logger.info(f"{r['id']} {r['title']} {r['score']}")