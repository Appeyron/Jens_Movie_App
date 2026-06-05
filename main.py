import movie_operations as mo


def main():
    """
    Start the movie database program and handle the main loop.
    """
    mo.show_menu(show_title=True)

    while True:
        chosen_option = mo.get_users_choice()
        should_continue = mo.execute_users_choice(chosen_option)

        if not should_continue:
            break


if __name__ == "__main__":
    main()