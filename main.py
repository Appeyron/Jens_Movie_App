import movie_operations as mo


def main():
    """Start the movie database program."""
    active_user = mo.select_user_profile()

    mo.show_menu(show_title=True, active_user=active_user)

    while True:
        chosen_option = mo.get_users_choice()
        result = mo.execute_users_choice(chosen_option, active_user)

        if result is False:
            break

        if result is not None:
            active_user = result


if __name__ == "__main__":
    main()