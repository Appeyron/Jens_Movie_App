"""
Movie database application.

Provides menu handling, movie management,
searching, filtering, statistics, and histogram creation.
"""

import random

from thefuzz import fuzz
from colorama import Fore, Style, init

from storage import movie_storage_sql as storage

MIN_MATCH_SCORE = 65

init(autoreset=True)

PROMPT_COLOR = Fore.WHITE
INPUT_COLOR = Fore.CYAN


def show_menu(wait_for_input=False, show_title=False):
    """
    Display the menu.
    Optionally wait for user input and/or show the title.
    """
    if wait_for_input:
        input(f"\n{Fore.YELLOW}Press enter to continue")

    if show_title:
        print(f"\n{Fore.YELLOW}** ** ** ** ** My Movies Database ** ** ** ** **")

    menu_text = (
        "\nMenu:\n"
        "0. Exit\n"
        "1. List movies\n"
        "2. Add movie\n"
        "3. Delete movie\n"
        "4. Stats\n"
        "5. Random movie\n"
        "6. Search movie\n"
        "7. Movies sorted by rating\n"
        "8. Generate website"
    )

    print(Fore.YELLOW + menu_text + Style.RESET_ALL)


def get_users_choice():
    """
    Ask the user to choose a menu option.
    Return the user input as a clean string.
    """
    print(f"\n{Fore.YELLOW}Enter choice (0-11):", end="")
    return input(f"{INPUT_COLOR}").strip()


def execute_users_choice(chosen_option):
    """
    Execute the function that belongs to the chosen menu option.
    Return False if the program should stop.
    """
    menu_dispatcher = {
        "1": list_movies,
        "2": add_movie,
        "3": delete_movie,
        "4": stats,
        "5": random_movie,
        "6": search_movie,
        "7": movies_sorted_by_rating,
        "8": generate_website
    }

    if chosen_option == "0":
        print(f"{PROMPT_COLOR}Bye!")
        return False

    if chosen_option in menu_dispatcher:
        try:
            menu_dispatcher[chosen_option]()
        except (
                ValueError,
                TypeError,
                KeyError,
                RuntimeError
        ) as error:
            print(f"{Fore.RED}Unexpected error: {error}")
    else:
        print(f"{Fore.RED}Invalid choice. Please enter a number from 0 to 11.")

    show_menu(wait_for_input=True)
    return True


def get_non_empty_title(prompt):
    """
    Ask for a movie title until the input is not empty.
    """
    while True:
        title = input(f"{PROMPT_COLOR}{prompt}{INPUT_COLOR}").strip()

        if title != "":
            return title

        print(f"{Fore.RED}Movie title must not be empty.")


def get_filename(prompt):
    """
    Ask for a filename until the input is not empty.
    """
    while True:
        filename = input(f"{PROMPT_COLOR}{prompt}{INPUT_COLOR}").strip()

        if filename != "":
            return filename

        print(f"{Fore.RED}Filename must not be empty.")


def get_chronological_order():
    """
    Ask whether latest movies should be shown first or last.
    Return True if latest movies should be first.
    """
    while True:
        print(f"{PROMPT_COLOR}How do you want to sort the movies?")
        print("1. Latest movies first")
        print("2. Latest movies last")

        choice = input(f"{PROMPT_COLOR}Enter choice (1-2): {INPUT_COLOR}").strip()

        if choice == "1":
            return True

        if choice == "2":
            return False

        print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.")


def list_movies():
    """
    Print all movies with year and rating.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    print(f"\n{PROMPT_COLOR}{len(movies)} movies in total\n")

    for title, movie_data in movies.items():
        print(
            f"{title}: "
            f"({movie_data['year']}), "
            f"{movie_data['rating']}"
        )


def add_movie():
    """
    Ask the user for movie data and add the movie to the JSON database.
    """
    movies = storage.list_movies()

    while True:
        title = get_non_empty_title("Enter new movie name: ")

        if title not in movies:
            break

        print(f"{Fore.RED}Movie {title} already exists!")

    storage.add_movie(title)


def delete_movie():
    """
    Ask the user for a movie title and delete it from the JSON database.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    while True:
        title = get_non_empty_title("Enter movie name to delete: ")

        if title in movies:
            break

        print(f"{Fore.RED}Movie {title} does not exist.")

    storage.delete_movie(title)


def stats():
    """
    Print statistics about the movie ratings.
    Display average and median with one decimal place.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    ratings = [
        movie_data["rating"]
        for movie_data in movies.values()
    ]

    average_rating = sum(ratings) / len(ratings)

    sorted_ratings = sorted(ratings)
    middle_index = len(sorted_ratings) // 2

    if len(sorted_ratings) % 2 != 0:
        median_rating = sorted_ratings[middle_index]
    else:
        median_rating = (
            sorted_ratings[middle_index - 1]
            + sorted_ratings[middle_index]
        ) / 2

    best_rating = max(ratings)
    worst_rating = min(ratings)

    best_movies = [
        title
        for title, movie_data in movies.items()
        if movie_data["rating"] == best_rating
    ]

    worst_movies = [
        title
        for title, movie_data in movies.items()
        if movie_data["rating"] == worst_rating
    ]

    print(f"\n{PROMPT_COLOR}Average rating: {average_rating:.1f}")
    print(f"Median rating: {median_rating:.1f}")

    print(
        f"Best movie(s): "
        f"{', '.join(best_movies)}, "
        f"{best_rating:.1f}"
    )

    print(
        f"Worst movie(s): "
        f"{', '.join(worst_movies)}, "
        f"{worst_rating:.1f}"
    )


def random_movie():
    """
    Print one random movie suggestion.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    title = random.choice(list(movies.keys()))
    movie_data = movies[title]

    print(
        f"\n{PROMPT_COLOR}Your movie for tonight: "
        f"{title} "
        f"({movie_data['year']}), "
        f"it's rated {movie_data['rating']}"
    )


def search_movie():
    """
    Search for movies by partial match.
    If no partial match is found, show similar movies with fuzzy matching.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    search_term = get_non_empty_title("\nEnter part of movie name: ").lower()

    matching_movies = []

    for title, movie_data in movies.items():
        if search_term in title.lower():
            matching_movies.append((title, movie_data))

    if matching_movies:
        print(f"\n{PROMPT_COLOR}Found matching movie(s):")

        for title, movie_data in matching_movies:
            print(
                f"{title} "
                f"({movie_data['year']}): "
                f"{movie_data['rating']}"
            )

        return

    fuzzy_matches = []

    for title, movie_data, match_score in fuzzy_matches:
        match_score = fuzz.token_set_ratio(search_term, title.lower())

        if match_score >= MIN_MATCH_SCORE:
            fuzzy_matches.append((title, movie_data, match_score))

    if not fuzzy_matches:
        print(f"{PROMPT_COLOR}No movie found, or similar.")
        return

    fuzzy_matches.sort(
        key=lambda match: match[2],
        reverse=True
    )

    print(f"{PROMPT_COLOR}Movie not exactly found, but similar ones:")

    for title, movie_data in fuzzy_matches:
        print(
            f"{title} "
            f"({movie_data['year']}): "
            f"{movie_data['rating']}"
        )


def movies_sorted_by_rating():
    """
    Print all movies sorted by rating from highest to lowest.
    """
    movies = storage.list_movies()

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda movie: movie[1]["rating"],
        reverse=True
    )

    print()

    for title, movie_data in sorted_movies:
        print(
            f"{title} "
            f"({movie_data['year']}): "
            f"{movie_data['rating']}"
        )


def generate_website():
    """Generate an HTML website from the movies database."""
    movies = storage.list_movies()

    with open("index_template.html", "r", encoding="utf-8") as file:
        template = file.read()

    movie_grid = ""

    for title, movie_data in movies.items():
        poster_url = movie_data.get("poster_url")
        year = movie_data.get("year")

        movie_grid += f"""
        <li>
            <div class="movie">
                <img class="movie-poster"
                     src="{poster_url}"/>
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
            </div>
        </li>
        """

    html_content = template.replace(
        "__TEMPLATE_MOVIE_GRID__",
        movie_grid
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Website was generated successfully")