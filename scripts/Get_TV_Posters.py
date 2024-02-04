import os
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import configparser

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('../config.cfg')

API_KEY = config['DEFAULT']['API_KEY']
TV_FOLDER_PATH = config['DEFAULT']['TV_FOLDER_PATH']

def search_tv_show(tv_show_name, release_year):
    url = "https://api.themoviedb.org/3/search/tv"
    params = {
        "query": tv_show_name,
        "include_adult": False,
        "language": "en-US",
        "page": 1,
        "first_air_date_year": release_year
    }

    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def download_tv_show_poster(tv_show_path, save_folder, tv_show_name):
    # Download Poster
    tv_show_name_cleaned = tv_show_name.replace(" ", "_")
    poster_url = f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{tv_show_path}"
    poster_filename = f"{tv_show_name_cleaned}.jpg"
    poster_save_path = os.path.join(save_folder, poster_filename)

    # Check if poster already exists
    if os.path.exists(poster_save_path):
        1==1
        #print(f"Poster already exists for {tv_show_name}")
    else:
        #print(f"Downloading poster for {tv_show_name}")
        poster_response = requests.get(poster_url)
        with open(poster_save_path, 'wb') as f:
            f.write(poster_response.content)

def process_tv_show(tv_show_folder):
    tv_show_path = os.path.join(TV_FOLDER_PATH, tv_show_folder)

    if os.path.isdir(tv_show_path):
        tv_show_name, release_year = tv_show_folder.split('(')
        release_year = release_year.strip(')')

        tv_show_data = search_tv_show(tv_show_name.strip(), release_year)

        if tv_show_data.get('results', []):
            poster_path_tmdb = tv_show_data['results'][0]['poster_path']
            download_tv_show_poster(poster_path_tmdb, tv_show_path, tv_show_name)
            

print(f"Checking TV Show Posters!")

# Get the total number of folders to process
total_folders = len(os.listdir(TV_FOLDER_PATH))

# Use tqdm for a simple loading bar
with tqdm(total=total_folders, desc="Progress") as pbar:
    def update_progress(*_):
        pbar.update()

    with ThreadPoolExecutor() as executor:
        # Process each folder concurrently
        executor.map(lambda x: (update_progress(process_tv_show(x))), os.listdir(TV_FOLDER_PATH))

print(f"Done!")
