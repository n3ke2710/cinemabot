from googlesearch import search # type: ignore


def search_first_result(movie_name, is_series: bool = False):
	if is_series:
		query = f"Сериал {movie_name} смотреть онлайн site:vkvideo.ru"
	else:
		query = f"Фильм {movie_name} смотреть онлайн site:vk.com | site:rutube.ru"
	for url in search(query, num_results=1, lang="ru"):
		return url
	return None
	