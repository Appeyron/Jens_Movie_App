"""
Movie storage module using SQLAlchemy, SQLite, and OMDb API.

Supports multiple user profiles.
Each movie belongs to one user.
"""

from pathlib import Path

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "movies.db"

DB_URL = f"sqlite:///{DB_PATH}"
OMDB_API_KEY = "57991dc6"
OMDB_URL = "https://www.omdbapi.com/"

engine = create_engine(DB_URL)

COUNTRY_FLAGS = {
    "USA": "🇺🇸",
    "United States": "🇺🇸",
    "UK": "🇬🇧",
    "United Kingdom": "🇬🇧",
    "Germany": "🇩🇪",
    "France": "🇫🇷",
    "Italy": "🇮🇹",
    "Spain": "🇪🇸",
    "Canada": "🇨🇦",
    "Australia": "🇦🇺",
    "Japan": "🇯🇵",
    "South Korea": "🇰🇷",
    "India": "🇮🇳",
    "China": "🇨🇳",
    "New Zealand": "🇳🇿",
    "Mexico": "🇲🇽",
    "Brazil": "🇧🇷",
    "Argentina": "🇦🇷",
    "Sweden": "🇸🇪",
    "Norway": "🇳🇴",
    "Denmark": "🇩🇰",
    "Finland": "🇫🇮",
    "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪",
    "Austria": "🇦🇹",
    "Switzerland": "🇨🇭",
    "Ireland": "🇮🇪",
    "Poland": "🇵🇱",
    "Russia": "🇷🇺",
}


def add_column_if_missing(connection, table_name, column_name, column_type):
    """Add a column to a table if the column does not exist yet."""
    result = connection.execute(text(f"PRAGMA table_info({table_name})"))
    existing_columns = [row[1] for row in result.fetchall()]

    if column_name not in existing_columns:
        connection.execute(
            text(f"""
                ALTER TABLE {table_name}
                ADD COLUMN {column_name} {column_type}
            """)
        )


COUNTRY_CODES = {
    "USA": "us",
    "United States": "us",
    "UK": "gb",
    "United Kingdom": "gb",
    "Germany": "de",
    "France": "fr",
    "Italy": "it",
    "Spain": "es",
    "Canada": "ca",
    "Australia": "au",
    "Japan": "jp",
    "South Korea": "kr",
    "India": "in",
    "China": "cn",
}


COUNTRY_CODES = {
    "USA": "us",
    "United States": "us",
    "UK": "gb",
    "United Kingdom": "gb",
    "Germany": "de",
    "France": "fr",
    "Italy": "it",
    "Spain": "es",
    "Canada": "ca",
    "Australia": "au",
    "Japan": "jp",
    "South Korea": "kr",
    "India": "in",
    "China": "cn",
}


def get_flag_from_country(country_text):
    """Return a flag image URL for the first country."""
    if not country_text or country_text == "N/A":
        return ""

    first_country = country_text.split(",")[0].strip()
    country_code = COUNTRY_CODES.get(first_country)

    if not country_code:
        return ""

    return f"https://flagcdn.com/w40/{country_code}.png"


with engine.connect() as connection:
    connection.execute(text("PRAGMA foreign_keys = ON"))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT,
            note TEXT,
            imdb_id TEXT,
            country TEXT,
            flag TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, title)
        )
    """))

    add_column_if_missing(connection, "movies", "note", "TEXT")
    add_column_if_missing(connection, "movies", "imdb_id", "TEXT")
    add_column_if_missing(connection, "movies", "country", "TEXT")
    add_column_if_missing(connection, "movies", "flag", "TEXT")

    connection.commit()


def list_users():
    """Retrieve all users from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, name
                FROM users
                ORDER BY name
            """)
        )

        users = result.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
        }
        for row in users
    ]


def add_user(name):
    """Add a new user profile."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    INSERT INTO users (name)
                    VALUES (:name)
                """),
                {"name": name},
            )

            connection.commit()

            return {
                "id": result.lastrowid,
                "name": name,
            }

    except IntegrityError:
        print(f"User '{name}' already exists.")
        return get_user_by_name(name)

    except SQLAlchemyError as error:
        print(f"Database error: {error}")
        return None


def get_user_by_name(name):
    """Retrieve one user by name."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, name
                FROM users
                WHERE name = :name
            """),
            {"name": name},
        )

        row = result.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
    }


def list_movies(user_id):
    """Retrieve all movies for one user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    title,
                    year,
                    rating,
                    poster_url,
                    note,
                    imdb_id,
                    country,
                    flag
                FROM movies
                WHERE user_id = :user_id
                ORDER BY title
            """),
            {"user_id": user_id},
        )

        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3],
            "note": row[4],
            "imdb_id": row[5],
            "country": row[6],
            "flag": row[7],
        }
        for row in movies
    }


def fetch_movie_from_omdb(title):
    """Fetch movie data from OMDb API by title."""
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
    }

    try:
        response = requests.get(OMDB_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            print(f"Movie '{title}' not found in OMDb.")
            return None

        imdb_rating = data.get("imdbRating")

        if imdb_rating == "N/A":
            imdb_rating = 0

        country = data.get("Country")
        flag = get_flag_from_country(country)

        return {
            "title": data.get("Title"),
            "year": int(data.get("Year", 0)[:4]),
            "rating": float(imdb_rating),
            "poster_url": data.get("Poster"),
            "imdb_id": data.get("imdbID"),
            "country": country,
            "flag": flag,
        }

    except requests.RequestException as error:
        print(f"OMDb request error: {error}")
        return None

    except ValueError as error:
        print(f"Data conversion error: {error}")
        return None


def add_movie(title, user_id, username):
    """Add a movie to one user's collection."""
    movie = fetch_movie_from_omdb(title)

    if movie is None:
        return

    movie["user_id"] = user_id

    try:
        with engine.connect() as connection:
            connection.execute(
                text("""
                    INSERT INTO movies (
                        user_id,
                        title,
                        year,
                        rating,
                        poster_url,
                        imdb_id,
                        country,
                        flag
                    )
                    VALUES (
                        :user_id,
                        :title,
                        :year,
                        :rating,
                        :poster_url,
                        :imdb_id,
                        :country,
                        :flag
                    )
                """),
                movie,
            )

            connection.commit()

        print(
            f"Movie '{movie['title']}' "
            f"added to {username}'s collection!"
        )

    except IntegrityError:
        print(
            f"Movie '{movie['title']}' "
            f"already exists in {username}'s collection."
        )

    except SQLAlchemyError as error:
        print(f"Database error: {error}")


def update_movie(title, rating, user_id):
    """Update a movie's rating for one user."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    UPDATE movies
                    SET rating = :rating
                    WHERE title = :title
                    AND user_id = :user_id
                """),
                {
                    "title": title,
                    "rating": rating,
                    "user_id": user_id,
                },
            )

            connection.commit()

            if result.rowcount > 0:
                print(f"Movie '{title}' updated successfully.")
            else:
                print(f"Movie '{title}' not found.")

    except SQLAlchemyError as error:
        print(f"Database error: {error}")


def update_movie_note(title, note, user_id):
    """Update a movie note for one user."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    UPDATE movies
                    SET note = :note
                    WHERE title = :title
                    AND user_id = :user_id
                """),
                {
                    "title": title,
                    "note": note,
                    "user_id": user_id,
                },
            )

            connection.commit()

            if result.rowcount > 0:
                print(f"Movie '{title}' successfully updated.")
            else:
                print(f"Movie '{title}' not found.")

    except SQLAlchemyError as error:
        print(f"Database error: {error}")


def delete_movie(title, user_id):
    """Delete a movie from one user's collection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    DELETE FROM movies
                    WHERE title = :title
                    AND user_id = :user_id
                """),
                {
                    "title": title,
                    "user_id": user_id,
                },
            )

            connection.commit()

            if result.rowcount > 0:
                print(f"Movie '{title}' deleted successfully.")
            else:
                print(f"Movie '{title}' not found.")

    except SQLAlchemyError as error:
        print(f"Database error: {error}")