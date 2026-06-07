"""
Movie storage module using SQLAlchemy, SQLite, and OMDb API.
"""

from pathlib import Path

import requests
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "movies.db"

DB_URL = f"sqlite:///{DB_PATH}"
OMDB_API_KEY = "57991dc6"
OMDB_URL = "https://www.omdbapi.com/"

engine = create_engine(DB_URL)  # , echo=True


with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster_url FROM movies")
        )
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster_url": row[3],
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

        return {
            "title": data.get("Title"),
            "year": int(data.get("Year", 0)),
            "rating": float(data.get("imdbRating", 0)),
            "poster_url": data.get("Poster"),
        }

    except requests.RequestException as error:
        print(f"OMDb request error: {error}")
        return None

    except ValueError as error:
        print(f"Data conversion error: {error}")
        return None


def add_movie(title):
    """Add a movie by fetching its data from OMDb."""
    movie = fetch_movie_from_omdb(title)

    if movie is None:
        return

    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster_url)
                    VALUES (:title, :year, :rating, :poster_url)
                """),
                movie,
            )

            connection.commit()
            print(f"Movie '{movie['title']}' added successfully.")

        except Exception as error:
            print(f"Error: {error}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("""
                    UPDATE movies
                    SET rating = :rating
                    WHERE title = :title
                """),
                {
                    "title": title,
                    "rating": rating,
                },
            )

            connection.commit()

            if result.rowcount > 0:
                print(f"Movie '{title}' updated successfully.")
            else:
                print(f"Movie '{title}' not found.")

        except Exception as error:
            print(f"Error: {error}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            result = connection.execute(
                text("""
                    DELETE FROM movies
                    WHERE title = :title
                """),
                {"title": title},
            )

            connection.commit()

            if result.rowcount > 0:
                print(f"Movie '{title}' deleted successfully.")
            else:
                print(f"Movie '{title}' not found.")

        except Exception as error:
            print(f"Error: {error}")