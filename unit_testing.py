from movie_storage_sql import list_movies, add_movie, update_movie, delete_movie

# Test listing movies
#movies = list_movies()
#print(movies)

# Test adding a movie
add_movie("Titanic")

# Test updating a movie's rating
#update_movie("Inception", 9.0)
print(list_movies())
#
# # Test deleting a movie
# delete_movie("Inception")
# print(list_movies())  # Should be empty if it was the only movie