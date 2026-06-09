"""
Movie database application.

Provides user profile handling, movie management,
searching, statistics, and website generation.
"""

import random

from colorama import Fore, Style, init
from thefuzz import fuzz

from storage import movie_storage_sql as storage

MIN_MATCH_SCORE = 65

init(autoreset=True)

PROMPT_COLOR = Fore.WHITE
INPUT_COLOR = Fore.CYAN


def select_user_profile():
    """Let the user select or create a user profile."""
    print(f"\n{Fore.YELLOW}Welcome to the Movie App!")

    while True:
        users = storage.list_users()

        print(f"\n{PROMPT_COLOR}Select a user:")

        for index, user in enumerate(users, start=1):
            print(f"{index}. {user['name']}")

        print(f"{len(users) + 1}. Create new user")

        choice = input(
            f"{PROMPT_COLOR}Enter choice: {INPUT_COLOR}"
        ).strip()

        if not choice.isdigit():
            print(f"{Fore.RED}Please enter a number.")
            continue

        choice_number = int(choice)

        if 1 <= choice_number <= len(users):
            selected_user = users[choice_number - 1]
            print(f"\n{PROMPT_COLOR}Welcome {selected_user['name']}!")
            return selected_user

        if choice_number == len(users) + 1:
            username = get_non_empty_input("Enter new username: ")
            new_user = storage.add_user(username)

            if new_user is not None:
                print(f"{PROMPT_COLOR}User '{username}' created.")
                return new_user

        print(f"{Fore.RED}Invalid choice.")


def show_menu(wait_for_input=False, show_title=False, active_user=None):
    """Display the menu."""
    if wait_for_input:
        input(f"\n{Fore.YELLOW}Press enter to continue")

    if show_title:
        print(f"\n{Fore.YELLOW}** ** ** My Movies Database ** ** **")

    username = active_user["name"] if active_user else "No user"

    menu_text = (
        f"\nActive user: {username}\n"
        "\nMenu:\n"
        "0. Exit\n"
        "1. List movies\n"
        "2. Add movie\n"
        "3. Delete movie\n"
        "4. Update movie\n"
        "5. Stats\n"
        "6. Random movie\n"
        "7. Search movie\n"
        "8. Movies sorted by rating\n"
        "9. Generate website\n"
        "10. Switch user"
    )

    print(Fore.YELLOW + menu_text + Style.RESET_ALL)


def get_users_choice():
    """Ask the user to choose a menu option."""
    print(f"\n{Fore.YELLOW}Enter choice (0-10):", end="")
    return input(f"{INPUT_COLOR}").strip()


def execute_users_choice(chosen_option, active_user):
    """Execute the selected menu option."""
    menu_dispatcher = {
        "1": list_movies,
        "2": add_movie,
        "3": delete_movie,
        "4": update_movie,
        "5": stats,
        "6": random_movie,
        "7": search_movie,
        "8": movies_sorted_by_rating,
        "9": generate_website,
    }

    if chosen_option == "0":
        print(f"{PROMPT_COLOR}Bye!")
        return False

    if chosen_option == "10":
        return select_user_profile()

    if chosen_option in menu_dispatcher:
        try:
            menu_dispatcher[chosen_option](active_user)
        except (
            ValueError,
            TypeError,
            KeyError,
            RuntimeError,
            FileNotFoundError,
        ) as error:
            print(f"{Fore.RED}Unexpected error: {error}")
    else:
        print(f"{Fore.RED}Invalid choice. Please enter a number from 0 to 10.")

    show_menu(wait_for_input=True, active_user=active_user)
    return None


def get_non_empty_input(prompt):
    """Ask for input until it is not empty."""
    while True:
        user_input = input(f"{PROMPT_COLOR}{prompt}{INPUT_COLOR}").strip()

        if user_input:
            return user_input

        print(f"{Fore.RED}Input must not be empty.")


def list_movies(active_user):
    """Print all movies of the active user."""
    movies = storage.list_movies(active_user["id"])

    if not movies:
        print(
            f"{Fore.RED}{active_user['name']}, "
            f"your movie collection is empty. Add some movies!"
        )
        return

    print(
        f"\n{PROMPT_COLOR}{active_user['name']}, "
        f"you have {len(movies)} movie(s):\n"
    )

    for title, movie_data in movies.items():
        note = movie_data.get("note") or "No note"

        print(
            f"{title}: "
            f"({movie_data['year']}), "
            f"{movie_data['rating']} "
            f"| Note: {note}"
        )


def add_movie(active_user):
    """Add a movie to the active user's collection."""
    movies = storage.list_movies(active_user["id"])

    while True:
        title = get_non_empty_input("Enter new movie name: ")

        if title not in movies:
            break

        print(f"{Fore.RED}Movie '{title}' already exists in your collection!")

    storage.add_movie(title, active_user["id"], active_user["name"])


def update_movie(active_user):
    """Add or update a note for a movie."""
    movies = storage.list_movies(active_user["id"])

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    title = get_non_empty_input("Enter movie name: ")

    if title not in movies:
        print(f"{Fore.RED}Movie '{title}' does not exist.")
        return

    note = get_non_empty_input("Enter movie note: ")

    storage.update_movie_note(title, note, active_user["id"])

    print(f"{PROMPT_COLOR}Movie '{title}' successfully updated.")


def delete_movie(active_user):
    """Delete a movie from the active user's collection."""
    movies = storage.list_movies(active_user["id"])

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    while True:
        title = get_non_empty_input("Enter movie name to delete: ")

        if title in movies:
            break

        print(f"{Fore.RED}Movie '{title}' does not exist.")

    storage.delete_movie(title, active_user["id"])


def stats(active_user):
    """Print rating statistics for the active user's movies."""
    movies = storage.list_movies(active_user["id"])

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
    print(f"Best movie(s): {', '.join(best_movies)}, {best_rating:.1f}")
    print(f"Worst movie(s): {', '.join(worst_movies)}, {worst_rating:.1f}")


def random_movie(active_user):
    """Print one random movie suggestion."""
    movies = storage.list_movies(active_user["id"])

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


def search_movie(active_user):
    """Search movies in the active user's collection."""
    movies = storage.list_movies(active_user["id"])

    if not movies:
        print(f"{Fore.RED}No movies found.")
        return

    search_term = get_non_empty_input("\nEnter part of movie name: ").lower()

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

    for title, movie_data in movies.items():
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

    for title, movie_data, match_score in fuzzy_matches:
        print(
            f"{title} "
            f"({movie_data['year']}): "
            f"{movie_data['rating']} "
            f"(match: {match_score}%)"
        )


def movies_sorted_by_rating(active_user):
    """Print movies sorted by rating."""
    movies = storage.list_movies(active_user["id"])

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


def generate_website(active_user):
    """Generate an HTML website for the active user."""
    movies = storage.list_movies(active_user["id"])

    with open("index_template.html", "r", encoding="utf-8") as file:
        template = file.read()

    movie_grid = ""

    for title, movie_data in movies.items():
        poster_url = movie_data.get("poster_url")
        year = movie_data.get("year")
        rating = movie_data.get("rating")
        note = movie_data.get("note") or ""


        note_html = ""

        if note:
            note_html = f'<div class="movie-note">{note}</div>'

        movie_grid += f"""
        <li>
            <div class="movie">
                <div class="poster-wrapper">
                    <img class="movie-poster"
                         src="{poster_url}"
                         alt="{title}"
                         title="{note}"/>
                    {note_html}
                </div>
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-rating">⭐ {rating}</div>
            </div>
        </li>
        """

    html_content = (
        template
        .replace("__TEMPLATE_MOVIE_GRID__", movie_grid)
        .replace("__USERNAME__", active_user["name"])
    )

    filename = f"{active_user['name']}_movies.html"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"{PROMPT_COLOR}Website '{filename}' was generated successfully.")