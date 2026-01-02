"""
Fuzzy search utility for track identification.
Uses RapidFuzz for efficient fuzzy matching.
"""

# Import searching libraries
from rapidfuzz import process, fuzz

# Import caching
from api.cache.redis_handler import RedisHandler

# Import dataset loader
from api.utils.load_dataset import load_dataset

# Initialize Redis cache handler
cache = RedisHandler(default_ttl=600)


class TrackSearcher:
    """
    Class to handle fuzzy searching of tracks.
    """

    def __init__(self):
        # Initialize dataset and candidates
        self.data = load_dataset() 
        self.tracks = self._build_candidates()

    def _build_candidates(self) -> list:
        """
        Build list of track candidates for fuzzy searching.

        Returns:
            list[dict]: List of track candidate dictionaries
        """
        tracks = []
        for mix in self.data:
            for track in mix.get("tracklist", []):
                candidate = f"{track.get('id','')} {track.get('title','')}"
                tracks.append({
                    "candidate": candidate,
                    "id": track.get("id"),
                    "title": track.get("title"),
                    "mix_id": mix.get("id"),
                })
        return tracks
    
    def search_track(self, query, top=5) -> list[dict]:
        """
        Perform a fuzzy search for tracks by ID or title.

        Args:
            query (str): Track ID or title (may be misspelled).
            top (int): Number of top results to return.

        Returns:
            list[dict]: List of top matching tracks, each with its score.
        """
        cache_key = cache.make_key("track_search", query, top)

        cached = cache.get(cache_key)
        if cached:
            return cached

        # List of candidates
        candidates = [t["candidate"] for t in self.tracks]
        
        # RapidFuzz search
        results = process.extract(
            query,
            candidates,
            scorer=fuzz.token_sort_ratio,
            limit=top
        )
        
        # Prepare results
        matches = []
        for _, score, idx in results:
            track_info = self.tracks[idx]
            track_info["score"] = score
            matches.append(track_info)
        
        cache.set(cache_key, matches)
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
    for r in results:
        print(r["id"], r["title"], r["score"])