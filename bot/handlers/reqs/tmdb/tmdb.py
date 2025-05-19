from handlers.reqs.tmdb.config import tmdb_api_key, base_url # type: ignore
import requests # type: ignore
import aiohttp

async def get_movie_details(movie_id):
	
	url = f"{base_url}movie/{movie_id}?api_key={tmdb_api_key}&language=en-US"

	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status == 200:
				data = await response.json()
				if 'results' in data:
						data['results'].sort(key=lambda x: x.get('vote_count', 0), reverse=True)
				return data[:5]
			else:
				return None

async def search_movie(movie_title, is_series):
	url = f"{base_url}search/movie?api_key={tmdb_api_key}&query={movie_title}"
	if is_series:
		url = f"{base_url}search/tv?api_key={tmdb_api_key}&query={movie_title}"
	print(url)
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status == 200:
				return await response.json()
			else:
				return None

async def get_top_movies():
    """
    Получает список из 10 самых популярных фильмов с TMDB API.
    """
    url = f"{base_url}movie/popular?api_key={tmdb_api_key}&language=en-US&page=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('results', [])[:10]  # Возвращаем только первые 10 фильмов
            else:
                return None