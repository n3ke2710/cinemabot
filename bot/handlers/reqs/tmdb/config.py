import os
from dotenv import load_dotenv

load_dotenv()

tmdb_api_key = os.getenv('TMDB_API_KEY')
base_url = "https://api.themoviedb.org/3/"