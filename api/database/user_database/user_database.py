"""
The main module for managing user database operations.
"""
# Import password hashing library
from argon2 import PasswordHasher, Type

# Import psycopg errors
import psycopg.errors

# Import regular expressions and other utilities
import re
import secrets
import string

# Import configuration constants
from api.config.config import (
    ARGON_TIME_COST,
    ARGON_MEMORY_COST,
    ARGON_PARALLELISM,
    ARGON_HASH_LENGTH,
    ARGON_SALT_LENGTH,
)
from api.config.config import PEPPER

# Import postgres connection pool
from api.database.postsgres_pool import postgres_pool


class UserDatabase:
    """Class to handle user database operations."""
    
    def __init__(self):
        """Initialize the user database connection."""
        self._ready = False
        self.schema = "users"
        self._chars = string.ascii_letters + string.digits # Characters for user ID generation

        self._ph = PasswordHasher(
            time_cost=ARGON_TIME_COST,
            memory_cost=ARGON_MEMORY_COST,
            parallelism=ARGON_PARALLELISM,
            hash_len=ARGON_HASH_LENGTH,
            salt_len=ARGON_SALT_LENGTH,
            type=Type.ID,
            encoding="utf-8",
        )

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
        """Create necessary tables in the user database."""
        with postgres_pool.get_connection() as conn:
            with conn.cursor() as cur:
                # Create users table
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.users (
                        user_id CHAR(16) PRIMARY KEY NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role_id INTEGER DEFAULT 1,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
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
                conn.commit()

    def _hash_password(self, password: str) -> str:
        """Hash a plaintext password."""
        if not PEPPER:
            raise ValueError("PEPPER is not set for password hashing.")
        
        # Add pepper to password
        peppered = password + PEPPER   

        # Return hashed password
        return self._ph.hash(peppered)
        
    def _generate_user_id(self, username: str) -> str:
        """
        Generate a unique user ID based on the username.
        Args:
            username: The username of the user.
        Returns:
            A unique user ID string.
        """
        username_part = username[:8].ljust(8, "X") # Take first 8 characters of username, pad with 'X' if shorter

        random_part = "".join(secrets.choice(self._chars) for _ in range(8)) # Generate 8 random characters
        
        return username_part + random_part # Combine to form user ID and return
    
    def _sanitize_username(self, username: str) -> str:
        """
        Sanitize the username by stripping whitespace and removing invalid characters.
        Args:
            username: The username to sanitize.
        Returns:
            The sanitized username. (str)
        """
        cleaned = re.sub(r"[^A-Za-z0-9_]", "", username) # Only allow alphanumeric characters and underscores
        return cleaned.lower()# Convert to lowercase for consistency

    def create_account(self, username: str, email: str, password: str) -> bool:
        """
        Create a new user account.
        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's plaintext password.
        Returns:
            True if account creation was successful, False otherwise.
        """
        sanitized_username = self._sanitize_username(username) # Sanitize username
        user_id = self._generate_user_id(sanitized_username) # Generate user ID
        hashed_password = self._hash_password(password) # Hash the password

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO {self.schema}.users (user_id, username, email, password)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (user_id, sanitized_username, email, hashed_password)
                    )
                    conn.commit()
            
                return True

            except psycopg.errors.UniqueViolation:
                from api.logger.logger import logger
                logger.info("Username or email already exists.")
                conn.rollback()
                return False
            except Exception as e:
                from api.logger.logger import logger
                logger.error(f"Error creating account: {e}")
                conn.rollback()
                return False

    def verify_password(self, hashed: str, password: str) -> bool:
        """Verify a plaintext password against a hashed password."""
        if not PEPPER:
            raise ValueError("PEPPER is not set for password verification.")
        
        # Add pepper to password
        peppered = password + PEPPER   

        try:
            valid = self._ph.verify(hashed, peppered)
            return valid
        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Password verification error: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user with their username and password.
        Args:
            username: The user's username.
            password: The user's plaintext password.
        Returns:
            True if authentication is successful, False otherwise.
        """
        try:
            sanitized_username = self._sanitize_username(username) # Sanitize username

            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT password FROM {self.schema}.users
                        WHERE username = %s;
                        """,
                        (sanitized_username,)
                    )
                    result = cur.fetchone()
                    
                    if result is None:
                        from api.logger.logger import logger
                        logger.info("User not found.")
                        return False
                    
                    stored_hashed_password = result["password"]

            return self.verify_password(stored_hashed_password, password)

        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Error during authentication: {e}")
            return False
        
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account by username.
        Args:
            user_id: The user_id of the account to delete.
        Returns:
            True if deletion was successful, False otherwise.
        """

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        DELETE FROM {self.schema}.users
                        WHERE user_id = %s;
                        """,
                        (user_id,)
                    )
                    conn.commit()
            
                return True

            except Exception as e:
                from api.logger.logger import logger
                logger.error(f"Error deleting user: {e}")
                conn.rollback()
                return False
        
    def modify_user(
        self, 
        user_id: str, 
        new_email: str | None = None, 
        new_password: str | None = None) -> bool:
        """
        Modify user details such as email, password, and profile information.
        Args:
            user_id: The user ID of the account to modify (primary identifier).
            new_email: The new email address (optional).
            new_password: The new plaintext password (optional).
        Returns:
            True if modification was successful, False otherwise.
        """
        user_updates = []
        user_params = []

        # Handle user table updates
        if new_email:
            user_updates.append("email = %s")
            user_params.append(new_email)
        if new_password:
            hashed_password = self._hash_password(new_password)
            user_updates.append("password = %s")
            user_params.append(hashed_password)

        if not user_updates:
            from api.logger.logger import logger
            logger.info("No updates provided.")
            return False

        with postgres_pool.get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    # Update users table if there are user updates
                    if user_updates:
                        user_params.append(user_id)
                        cur.execute(
                            f"""
                            UPDATE {self.schema}.users
                            SET {', '.join(user_updates)}
                            WHERE user_id = %s;
                            """,
                            tuple(user_params)
                        )
                    
                    conn.commit()
            
                return True

            except Exception as e:
                from api.logger.logger import logger
                logger.error(f"Error modifying user: {e}")
                conn.rollback()
                return False

    def get_user_by_id(self, user_id: str) -> dict | None:
        """
        Retrieve user information by user ID.
        Args:
            user_id: The user ID to look up.
        Returns:
            A dictionary with user information if found, None otherwise.
        """
        try:
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT user_id, username, role_id, email, password FROM {self.schema}.users
                        WHERE user_id = %s;
                        """,
                        (user_id,)
                    )
                    result = cur.fetchone()
                    
                    return result if result else None

        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Error retrieving user by ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> dict | None:
        """
        Retrieve user information by username.
        Args:
            username: The username to look up.
        Returns:
            A dictionary with user information if found, None otherwise.
        """
        try:
            sanitized_username = self._sanitize_username(username) # Sanitize username

            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT user_id, username, role_id, email, password FROM {self.schema}.users
                        WHERE username = %s;
                        """,
                        (sanitized_username,)
                    )   
                    result = cur.fetchone()
                    
                    return result if result else None

        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Error retrieving user by username: {e}")
            return None

    def get_user_by_email(self, email: str) -> dict | None:
        """
        Retrieve user information by email.
        Args:
            email: The email to look up.
        Returns:
            A dictionary with user information if found, None otherwise.
        """
        try:
            with postgres_pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT user_id, username, role_id, email, password FROM {self.schema}.users
                        WHERE email = %s;
                        """,
                        (email,)
                    )
                    result = cur.fetchone()
                    
                    return result if result else None

        except Exception as e:
            from api.logger.logger import logger
            logger.error(f"Error retrieving user by email: {e}")
            return None

    def is_ready(self) -> bool:
        """
        Check if the user database is initialized and ready.
        Returns:
            True if the database is ready, False otherwise.
        """
        return self._ready

# Global singleton instance
user_database = UserDatabase()

# Initialize the database instance
user_database.init_db()