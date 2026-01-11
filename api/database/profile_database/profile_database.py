"""
The main module for managing profile database operations."""

# Import psycopg errors
import psycopg.errors

# Import postgres connection pool
from api.database.postsgres_pool import postgres_pool

# Import config values
from api.config.config import PROFILE_DEFAULT_BIO, PROFILE_DEFAULT_AVATAR_URL

class ProfileDatabase:
    """
    Class to handle profile database operations.
    Note: The class does not support a delete operation because profiles are automatically deleted
    via a foreign key constraint when a user is deleted from the users table.
    Note: This class depends on UserDatabase for user-related operations.
    """
    
    def __init__(self):
        """Initialize the profile database connection."""
        self._ready = False
        self.schema = "users"

    def init_db(self, schema: str = "users") -> bool: # Arguent nut needed but keept for cases where you have to rerout database data to fix issues etc.
        """Initialize the profile database schema."""
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
        """Create necessary tables in the profile database."""
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Create profiles table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.profiles (
                        user_id CHAR(16) PRIMARY KEY NOT NULL,
                        bio TEXT,
                        avatar_url TEXT,
                        prefered_bpm_range INT4RANGE,
                        prefered_genres TEXT[],
                        FOREIGN KEY (user_id) REFERENCES {self.schema}.users(user_id) ON DELETE CASCADE
                    );
                    """
                )
                # Create trigger function to auto-create profile on user creation
                cur.execute(
                    f"""
                    CREATE OR REPLACE FUNCTION {self.schema}.create_user_profile()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        -- This trigger function is executed automatically
                        -- after a new row is inserted into the users table.
                        -- NEW contains the newly inserted users row.
                        INSERT INTO {self.schema}.profiles (user_id, avatar_url, bio)
                        VALUES (
                            NEW.user_id, -- Same user_id as in users table
                            '{PROFILE_DEFAULT_AVATAR_URL}' || NEW.username, -- Auto-generated avatar using Dicebear
                            '{PROFILE_DEFAULT_BIO}' -- Default bio text
                        );
                        -- Required return value for AFTER INSERT triggers
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    """
                )
                # Create trigger to call the function after user insertion
                cur.execute(
                    f"""
                    -- Drop the trigger if it already exists to avoid duplicates
                    DROP TRIGGER IF EXISTS after_user_insert ON {self.schema}.users;

                    -- Create a trigger that runs after every INSERT on users.users
                    CREATE TRIGGER after_user_insert
                    AFTER INSERT ON {self.schema}.users
                    FOR EACH ROW
                    EXECUTE FUNCTION {self.schema}.create_user_profile();
                    """
                )
                conn.commit()

    def modify_user_profile(self, user_id: str, bio: str | None = None, avatar_url: str | None = None,
                            prefered_bpm_range: list[int] | None = None, prefered_genres: list[str] | None = None) -> bool:
        """ Modify user profile information.
        Args:
            user_id: The user ID whose profile is to be modified.
            bio: New bio text.
            avatar_url: New avatar URL.
            prefered_bpm_range: New preferred BPM range as a list [min, max].
            prefered_genres: New list of preferred genres.
        Returns:
            True if the profile was successfully updated, False otherwise.
        """
        profile_updates = []
        profile_params = []

        if bio is not None: # Allow empty string to clear bio
            profile_updates.append("bio = %s")
            profile_params.append(bio)
        if avatar_url is not None:
            profile_updates.append("avatar_url = %s")
            profile_params.append(avatar_url)
        if prefered_bpm_range is not None:
            # Convert tuple to PostgreSQL int4range format
            profile_updates.append("prefered_bpm_range = int4range(%s, %s)")
            profile_params.extend(prefered_bpm_range)
        if prefered_genres is not None:
            profile_updates.append("prefered_genres = %s")
            profile_params.append(prefered_genres)

        if not profile_updates:
            from api.logger.logger import logger
            logger.info("No profile fields to update.")
            return False
            
        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    profile_params.append(user_id)
                    cur.execute(
                        f"""
                        UPDATE {self.schema}.profiles
                        SET {', '.join(profile_updates)}
                        WHERE user_id = %s;
                        """,
                        tuple(profile_params)
                    )

                conn.commit()

                return True
        
            except Exception as e:
                from api.logger.logger import logger
                logger.error(f"Error modifying user profile: {e}")
                conn.rollback()
                return False

    def get_user_profile(self, user_id: str) -> dict | None:
        """
        Retrieve user profile information by user ID.
        Args:
            user_id: The user ID to look up.
        Returns:
            A dictionary with profile information if found, None otherwise.
        """
        try:
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT
                            p.user_id,
                            u.username,
                            p.bio,
                            p.avatar_url,
                            lower(p.prefered_bpm_range) AS bpm_min,
                            upper(p.prefered_bpm_range) AS bpm_max,
                            p.prefered_genres
                        FROM {self.schema}.profiles p
                        JOIN {self.schema}.users u ON p.user_id = u.user_id
                        WHERE p.user_id = %s;
                        """,
                        (user_id,)
                    )

                    row = cur.fetchone()
                    if not row:
                        return None

                    result = {
                        "user_id": row["user_id"],
                        "username": row["username"],
                        "bio": row["bio"],
                        "avatar_url": row["avatar_url"],
                        "prefered_genres": row["prefered_genres"],
                    }

                    bpm_min = row["bpm_min"]
                    bpm_max = row["bpm_max"]

                    result["prefered_bpm_range"] = (
                        [bpm_min, bpm_max]
                        if bpm_min is not None and bpm_max is not None
                        else None
                    )

                    return result

        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Error retrieving user profile: {e}")
            return None
        
    def is_ready(self) -> bool:
        """
        Check if the profile database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready

# Global singleton instance   
profile_database = ProfileDatabase()

# Initialize the database instance
profile_database.init_db()