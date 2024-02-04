import os
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import configparser

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('../config.cfg')

API_KEY = config['DEFAULT']['API_KEY']
FILMS_FOLDER_PATH = config['DEFAULT']['FILMS_FOLDER_PATH']

def search_movie(movie_name, release_year):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "query": movie_name,
        "include_adult": False,
        "language": "en-US",
        "page": 1,
        "year": release_year
    }

    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def download_poster_and_banner(media_path, save_folder, film_folder):
    # Download Poster
    poster_url = f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{media_path}"
    poster_filename = f"{film_folder}.jpg"
    poster_save_path = os.path.join(save_folder, poster_filename)

    # Check if poster already exists
    if not os.path.exists(poster_save_path):
        poster_response = requests.get(poster_url)
        with open(poster_save_path, 'wb') as f:
            f.write(poster_response.content)

    # Download Banner
    banner_url = f"https://www.themoviedb.org/t/p/w1280_and_h720_bestv2/{media_path}"
    banner_filename = f"{film_folder}_banner.jpg"
    banner_save_path = os.path.join(save_folder, banner_filename)

    # Check if banner already exists
    if not os.path.exists(banner_save_path):
        banner_response = requests.get(banner_url)
        with open(banner_save_path, 'wb') as f:
            f.write(banner_response.content)

def process_folder(film_folder):
    film_path = os.path.join(FILMS_FOLDER_PATH, film_folder)

    if os.path.isdir(film_path):
        movie_name, release_year = film_folder.split('(')
        release_year = release_year.strip(')')

        movie_data = search_movie(movie_name.strip(), release_year)

        if movie_data.get('results', []):

            poster_path_tmdb = movie_data['results'][0]['poster_path']
            download_poster_and_banner(poster_path_tmdb, film_path, film_folder)
            #print(f"Downloaded poster and banner for {film_folder}")

print(f"Checking Film Posters!")

# Get the total number of folders to process
total_folders = len(os.listdir(FILMS_FOLDER_PATH))

# Use tqdm for a simple loading bar
with tqdm(total=total_folders, desc="Progress") as pbar:
    def update_progress(*_):
        pbar.update()

    with ThreadPoolExecutor() as executor:
        # Process each folder concurrently
        executor.map(lambda x: (update_progress(process_folder(x))), os.listdir(FILMS_FOLDER_PATH))

print(f"Done!")
