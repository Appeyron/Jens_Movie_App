from storage import movie_storage_sql as storage


# Test listing movies
movies = storage.list_movies()
print(movies)

# Test adding a movie
#storage.add_movie("Titanic")

# Test updating a movie's rating
#update_movie("Inception", 9.0)
#print(storage.list_movies())
#
# Test deleting a movie
# storage.delete_movie("Inception")
# print(storage.list_movies())  # Should be empty if it was the only movie