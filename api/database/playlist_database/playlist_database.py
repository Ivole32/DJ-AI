"""
The main module for managing playlist database operations.
"""
# Import psycopg errors
import psycopg.errors

# Import postgres connection pool
from api.database.postsgres_pool import postgres_pool

# Import config values
from api.config.config import PLAYLIST_SORT_GAP, PLAYLIST_MIN_GAP

# Import utility to get track metadata
from api.utils.track_metadata import get_track_metadata

class PlaylistDatabase:
    """Class to handle playlist database operations."""
    
    def __init__(self):
        """Initialize the playlist database connection."""
        self._ready = False
        self.schema = "users"

    def init_db(self, schema: str = "users") -> bool: # Arguent nut needed but keept for cases where you have to rerout database data to fix issues etc.
        """Initialize the user database schema."""
        try:
            self.schema = schema
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")
                    conn.commit()
            self._create_tables()

            self._ready = True
            return True
    
        except psycopg.Error as e:
            from api.logger.logger import logger
            logger.error(f"Database error: {e}")
            return False
        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Unexpected error: {e}")
            return False

    def _create_tables(self) -> None:
        """Create necessary tables in the playlist database."""
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Create playlist table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.playlist (
                        playlist_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id CHAR(16) NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        tags TEXT[],
                        public BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT now(),

                        FOREIGN KEY (user_id)
                            REFERENCES {self.schema}.users(user_id)
                            ON DELETE CASCADE
                    );
                    """
                )
                # Create playlist_track table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.playlist_track (
                        playlist_track_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        playlist_id UUID NOT NULL REFERENCES {self.schema}.playlist(playlist_id) ON DELETE CASCADE,
                        youtube_track_id TEXT NOT NULL,
                        title TEXT,
                        artist TEXT,
                        bpm REAL,
                        key TEXT,
                        camelot TEXT,
                        energy REAL,
                        sort_key NUMERIC(20, 10) NOT NULL,
                        added_at TIMESTAMP NOT NULL DEFAULT now()
                    );
                    """
                )

                # Create indexes for faster lookups
                # Index on user_id in playlist table
                cur.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_playlist_user
                    ON {self.schema}.playlist(user_id);
                    """
                )

                # Index on playlist_id in playlist_track table
                cur.execute(
                    f""" 
                    CREATE INDEX IF NOT EXISTS idx_playlist_track_playlist
                    ON {self.schema}.playlist_track(playlist_id);
                    """
                )

                # Index on sort_key in playlist_track table for efficient ordering
                cur.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_playlist_track_order
                    ON {self.schema}.playlist_track (playlist_id, sort_key);
                    """
                )

                conn.commit()

    def _rebalance(self, cur, playlist_id: str):
        """Rebalance all sort_keys in a playlist to maintain proper spacing.
        
        This is called when the gap between adjacent tracks becomes too small (< PLAYLIST_MIN_GAP).
        Uses SQL window functions to efficiently renumber all tracks with proper spacing.
        
        Algorithm:
        1. Create subquery that assigns row numbers (1, 2, 3...) to all tracks ordered by current sort_key
        2. Multiply each row number by PLAYLIST_SORT_GAP to create evenly spaced sort_keys
        3. Update all tracks in single query using JOIN on playlist_track_id
        
        Example: If tracks have sort_keys [1.0, 1.01, 1.02] (gaps too small)
                 After rebalancing: [1000.0, 2000.0, 3000.0] (proper gaps restored)
        
        Args:
            cur: Active database cursor
            playlist_id: ID of the playlist to rebalance
        """
        cur.execute(
            f"""
            UPDATE {self.schema}.playlist_track
            SET sort_key = sub.rn * %s
            FROM (
                SELECT playlist_track_id,
                    row_number() OVER (
                        PARTITION BY playlist_id
                        ORDER BY sort_key
                    ) AS rn
                FROM {self.schema}.playlist_track
                WHERE playlist_id = %s
            ) AS sub
            WHERE {self.schema}.playlist_track.playlist_track_id = sub.playlist_track_id;
            """,
            (PLAYLIST_SORT_GAP, playlist_id)
        )

    def user_modify_allowed(self, playlist_id: str, user_id: str) -> bool:
        """
        Check if a playlist belongs to a specific user.
        Args:
            playlist_id: The ID of the playlist to check.
            user_id: The ID of the user to verify ownership.
        Returns:
            True if the playlist belongs to the user, False otherwise.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT 1 FROM {self.schema}.playlist
                    WHERE playlist_id = %s AND user_id = %s;
                    """,
                    (playlist_id, user_id)
                )
                return cur.fetchone() is not None
            
    def is_playlist_public(self, playlist_id: str) -> bool:
        """
        Check if a playlist is public.
        Args:
            playlist_id: The ID of the playlist to check.
        Returns:
            True if the playlist is public, False otherwise.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT public FROM {self.schema}.playlist
                    WHERE playlist_id = %s;
                    """,
                    (playlist_id,)
                )
                row = cur.fetchone()
                if row:
                    return row["public"]
                return False

    def create_playlist(self, user_id: str, name: str, description: str = None, tags: list[str] = None, public: bool = False) -> str:
        """
        Create a new playlist for a user.
        Args:
            user_id: The ID of the user creating the playlist.
            name: The name of the new playlist.
            description: Optional description of the playlist.
            tags: Optional list of tags for the playlist.
            public: Whether the playlist is public.
        Returns:
            The ID of the newly created playlist.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.playlist (user_id, name, description, tags, public)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING playlist_id;
                    """,
                    (user_id, name, description, tags, public)
                )
                playlist_id = cur.fetchone()['playlist_id']
                conn.commit()
                return str(playlist_id)
            
    def delete_playlist(self, playlist_id: str, user_id: str) -> bool:
        """
        Delete a playlist by its ID.
        Args:
            playlist_id: The ID of the playlist to delete.
        Returns:
            True if the playlist was deleted, False if unauthorized and None if not found.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Attempt to delete the playlist only if it belongs to the user
                cur.execute(
                    f"""
                    DELETE FROM {self.schema}.playlist
                    WHERE playlist_id = %s AND user_id = %s;
                    """,
                    (playlist_id, user_id)
                )
                if cur.rowcount > 0:
                    conn.commit()
                    return True # Successfully deleted

                # Check if the playlist exists
                cur.execute(
                    f"""
                    SELECT 1 FROM {self.schema}.playlist
                    WHERE playlist_id = %s;
                    """, 
                    (playlist_id,)
                )
                exists = cur.fetchone() is not None
                conn.rollback() # Rollback since no changes were made

                if exists:
                    return False  # Unauthorized
                else:
                    return None  # Not found
    
    def update_playlist(self, playlist_id: str, user_id: str, name: str = None, description: str = None, 
                       tags: list[str] = None, public: bool = None) -> bool:
        """
        Update a playlist's metadata.
        Args:
            playlist_id: The ID of the playlist to update.
            user_id: The ID of the user (for authorization).
            name: New name for the playlist (optional).
            description: New description for the playlist (optional).
            tags: New tags for the playlist (optional).
            public: New public status (optional).
        Returns:
            True if the playlist was successfully updated, False otherwise.
        """
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if tags is not None:
            updates.append("tags = %s")
            params.append(tags)
        if public is not None:
            updates.append("public = %s")
            params.append(public)

        if not updates:
            return False  # No fields to update

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    params.extend([playlist_id, user_id])
                    cur.execute(
                        f"""
                        UPDATE {self.schema}.playlist
                        SET {', '.join(updates)}
                        WHERE playlist_id = %s AND user_id = %s;
                        """,
                        tuple(params)
                    )
                    success = cur.rowcount > 0
                    conn.commit()
                    return success
            except Exception as e:
                from api.logger.logger import logger
                logger.error(f"Error updating playlist: {e}")
                conn.rollback()
                return False
                
    def get_users_playlists(self, user_id: str, include_private: bool) -> list[dict]:
        """
        Retrieve all playlists for a given user, including track count.
        Args:
            user_id: The ID of the user whose playlists to retrieve.
        Returns:
            A list of dictionaries containing playlist information and track count.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT p.playlist_id, p.name, p.description, p.tags, p.public, p.created_at,
                        (SELECT COUNT(*) FROM {self.schema}.playlist_track t WHERE t.playlist_id = p.playlist_id) AS tracks_count
                    FROM {self.schema}.playlist p
                    WHERE p.user_id = %s AND (p.public = TRUE OR %s = TRUE);
                    """,
                    (user_id, include_private)
                )
                rows = cur.fetchall()
                playlists = [
                    {
                        "playlist_id": str(row["playlist_id"]),
                        "name": row["name"],
                        "description": row["description"],
                        "tags": row["tags"] or [],
                        "public": row["public"],
                        "created_at": row["created_at"],
                        "tracks_count": row["tracks_count"]
                    }
                    for row in rows
                ]
                return playlists

    def get_playlist_by_id(self, playlist_id: str) -> dict | None:
        """
        Retrieve a playlist by its ID.
        Args:
            playlist_id: The ID of the playlist to retrieve.
        Returns:
            A dictionary containing playlist information, or None if not found.
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT playlist_id, user_id, name, description, tags, public, created_at
                    FROM {self.schema}.playlist
                    WHERE playlist_id = %s;
                    """,
                    (playlist_id,)
                )
                row = cur.fetchone()
                if row:
                    return {
                        "playlist_id": str(row["playlist_id"]),
                        "user_id": row["user_id"],
                        "name": row["name"],
                        "description": row["description"],
                        "tags": row["tags"] or [],
                        "public": row["public"],
                        "created_at": row["created_at"]
                    }
                return None

    def add_track_to_end(self, playlist_id: str, youtube_track_id: str) -> bool:
        """Append a track to the end of a playlist.
        
        Automatically calculates the sort_key by finding the maximum current sort_key
        and adding PLAYLIST_SORT_GAP (1000.0). Includes overflow protection to prevent
        sort_keys from exceeding 1e10.
        
        Overflow Protection:
        - If last_sort + PLAYLIST_SORT_GAP > 1e10, triggers rebalancing
        - Resets all sort_keys to evenly spaced values starting from PLAYLIST_SORT_GAP
        - Prevents NUMERIC overflow in PostgreSQL
        
        Metadata Loading:
        - Automatically loads title, artist, bpm, key, energy from dataset
        - Returns False if track not found in dataset
        - No need to pass metadata from frontend
        
        Args:
            playlist_id: The ID of the playlist.
            youtube_track_id: The YouTube ID of the track to add.
        Returns:
            True if the track was added successfully, False if metadata not found.
        """
        # Load track metadata from dataset
        metadata = get_track_metadata(youtube_track_id)
        
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT sort_key
                    FROM {self.schema}.playlist_track
                    WHERE playlist_id = %s
                    ORDER BY sort_key DESC
                    LIMIT 1;
                    """,
                    (playlist_id,)
                )

                row = cur.fetchone()
                if row:
                    last_sort = row["sort_key"]
                    # Check if we need to rebalance to prevent overflow
                    if last_sort + PLAYLIST_SORT_GAP > 1e10:
                        self._rebalance(cur, playlist_id)
                        cur.execute(
                            f"""
                            SELECT sort_key
                            FROM {self.schema}.playlist_track
                            WHERE playlist_id = %s
                            ORDER BY sort_key DESC
                            LIMIT 1;
                            """,
                            (playlist_id,)
                        )
                        row = cur.fetchone()
                        last_sort = row["sort_key"] if row else 0
                    new_sort = last_sort + PLAYLIST_SORT_GAP
                else:
                    new_sort = PLAYLIST_SORT_GAP

                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.playlist_track
                    (playlist_id, youtube_track_id, title, artist, bpm, key, camelot, energy, sort_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (playlist_id, youtube_track_id, metadata['title'], metadata['artist'], 
                     metadata['bpm'], metadata['key'], metadata['camelot'], metadata['energy'], new_sort)
                )
                if cur.rowcount == 0:
                    conn.rollback()
                    return False

            conn.commit()
            return True

    def add_track_to_start(self, playlist_id: str, youtube_track_id: str) -> bool:
        """
        Add a track to the start of a playlist.
        Args:
            playlist_id: The ID of the playlist.
            youtube_track_id: The YouTube ID of the track to add.
        Returns:
            True if the track was added successfully, False otherwise.
        """
        # Load track metadata from dataset
        metadata = get_track_metadata(youtube_track_id)
        
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    f"""
                    SELECT sort_key
                    FROM {self.schema}.playlist_track
                    WHERE playlist_id = %s
                    ORDER BY sort_key ASC
                    LIMIT 1;
                    """,
                    (playlist_id,)
                )

                row = cur.fetchone()
                if row:
                    first_sort = row["sort_key"]
                    new_sort = first_sort / 2
                    # Check if sort_key is getting too small
                    if new_sort < PLAYLIST_MIN_GAP:
                        self._rebalance(cur, playlist_id)
                        cur.execute(
                            f"""
                            SELECT sort_key
                            FROM {self.schema}.playlist_track
                            WHERE playlist_id = %s
                            ORDER BY sort_key ASC
                            LIMIT 1;
                            """,
                            (playlist_id,)
                        )
                        row = cur.fetchone()
                        first_sort = row["sort_key"] if row else PLAYLIST_SORT_GAP
                        new_sort = first_sort / 2
                else:
                    new_sort = PLAYLIST_SORT_GAP

                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.playlist_track
                    (playlist_id, youtube_track_id, title, artist, bpm, key, camelot, energy, sort_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (playlist_id, youtube_track_id, metadata['title'], metadata['artist'], 
                     metadata['bpm'], metadata['key'], metadata['camelot'], metadata['energy'], new_sort)
                )

                if cur.rowcount == 0:
                    conn.rollback()
                    return False
                
            conn.commit()
            return True

    def add_track_between(
        self,
        playlist_id: str,
        youtube_track_id: str,
        prev_sort: float,
        next_sort: float
    ) -> bool:
        """Insert a track between two existing tracks using fractional indexing.
        
        Calculates a sort_key that places the new track between prev_sort and next_sort.
        If the gap is too small (< PLAYLIST_MIN_GAP = 0.1), triggers automatic rebalancing
        to restore proper spacing throughout the entire playlist.
        
        Fractional Indexing:
        - Allows inserting tracks without renumbering all subsequent tracks
        - new_sort_key = (prev_sort + next_sort) / 2.0
        - Example: Insert between 1000.0 and 2000.0 → new sort_key = 1500.0
        
        Rebalancing:
        - Triggered when gap < 0.1 (e.g., prev=1000.0, next=1000.05)
        - Redistributes all sort_keys with PLAYLIST_SORT_GAP spacing
        - Maintains relative order of all tracks
        
        Args:
            playlist_id: The ID of the playlist.
            youtube_track_id: The YouTube ID of the track to add.
            prev_sort: The sort_key of the track before the new track.
            next_sort: The sort_key of the track after the new track.
        Raises:
            ValueError: If prev_sort is not less than next_sort.
        Returns:
            True if the track was added successfully, False if metadata not found.
        """
        # Load track metadata from dataset
        metadata = get_track_metadata(youtube_track_id)
        
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:

                if next_sort - prev_sort < PLAYLIST_MIN_GAP:
                    self._rebalance(cur, playlist_id)

                    # Find the new prev_sort and next_sort values after rebalancing
                    cur.execute(
                        f"""
                        SELECT sort_key
                        FROM {self.schema}.playlist_track
                        WHERE playlist_id = %s AND sort_key <= %s
                        ORDER BY sort_key DESC
                        LIMIT 1;
                        """,
                        (playlist_id, prev_sort)
                    )
                    prev_row = cur.fetchone()
                    
                    cur.execute(
                        f"""
                        SELECT sort_key
                        FROM {self.schema}.playlist_track
                        WHERE playlist_id = %s AND sort_key >= %s
                        ORDER BY sort_key ASC
                        LIMIT 1;
                        """,
                        (playlist_id, next_sort)
                    )
                    next_row = cur.fetchone()
                    
                    if prev_row and next_row:
                        prev_sort = prev_row["sort_key"]
                        next_sort = next_row["sort_key"]

                new_sort = (prev_sort + next_sort) / 2

                cur.execute(
                    f"""
                    INSERT INTO {self.schema}.playlist_track
                    (playlist_id, youtube_track_id, title, artist, bpm, key, camelot, energy, sort_key)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (playlist_id, youtube_track_id, metadata['title'], metadata['artist'], 
                     metadata['bpm'], metadata['key'], metadata['camelot'], metadata['energy'], new_sort)
                )

                if cur.rowcount == 0:
                    conn.rollback()
                    return False
                
                conn.commit()
                return True

    def get_tracks(self, playlist_id: str) -> list:
        """Retrieve all tracks from a playlist ordered by sort_key.
        
        Returns complete track metadata including technical data (bpm, key, camelot, energy)
        and positional data (sort_key, playlist_track_id) required for frontend display
        and track reordering operations.
        
        Return Fields:
        - playlist_track_id: Unique ID for deletion operations
        - youtube_track_id: YouTube video ID
        - title: Track title (from dataset.json)
        - artist: Artist name (from dataset.json)
        - bpm: Beats per minute (from tracks.csv)
        - key: Musical key, e.g., '6A', 'Cm' (from tracks.csv)
        - camelot: Camelot notation (from tracks.csv)
        - energy: Energy level 0.0-1.0 (from tracks.csv)
        - sort_key: Numeric position for ordering
        
        Args:
            playlist_id: The ID of the playlist.
        Returns:
            List of track dictionaries ordered by sort_key ASC (first to last).
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT playlist_track_id, youtube_track_id, title, artist, bpm, key, camelot, energy, sort_key
                    FROM {self.schema}.playlist_track
                    WHERE playlist_id = %s
                    ORDER BY sort_key ASC;
                    """,
                    (playlist_id,)
                )
                return cur.fetchall()
            
    def delete_track_from_playlists(self, playlist_track_id: str, playlist_id: str) -> int:
        """Remove a track from a playlist.
        
        Uses playlist_track_id (not youtube_track_id) to allow the same track
        to appear multiple times in a playlist if desired.
        
        Args:
            playlist_track_id: Unique ID of the track entry to delete
            playlist_id: ID of the playlist (for security/validation)
        Returns:
            True if a track was deleted, False if not found
        """
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    DELETE FROM {self.schema}.playlist_track
                    WHERE playlist_track_id = %s
                    AND playlist_id = %s;
                    """,
                    (playlist_track_id, playlist_id)
                )
                conn.commit()
                return cur.rowcount > 0

    def is_ready(self) -> bool:
        """
        Check if the playlist database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready

# Global singleton instance
playlist_database = PlaylistDatabase()

# Initialize the database instance
playlist_database.init_db()