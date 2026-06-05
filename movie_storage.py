"""
Movie storage module.

Provides functions to load, save, add, update,
and delete movies in a JSON file.
"""


import json

MOVIES_FILE = "movies.json"


def get_movies():
    """
    Load and return all movies from the JSON file.
    """
    try:
        with open(MOVIES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_movies(movies):
    """
    Save all movies to the JSON file.
    """
    with open(MOVIES_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, indent=4)


def add_movie(title, year, rating):
    """
    Add a movie to the JSON database.
    """
    movies = get_movies()

    movies[title] = {
        "year": year,
        "rating": rating
    }

    save_movies(movies)


def delete_movie(title):
    """
    Delete a movie from the JSON database.
    """
    movies = get_movies()

    if title in movies:
        del movies[title]

    save_movies(movies)


def update_movie(title, rating):
    """
    Update the rating of a movie in the JSON database.
    """
    movies = get_movies()

    if title in movies:
        movies[title]["rating"] = rating

    save_movies(movies)
