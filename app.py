from flask import Flask, render_template, send_file, abort, request, make_response, redirect, url_for, jsonify
import os
import subprocess
import socket
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from security import block_bad_connections, remove_old_cookies, log_bad_connection, log_connection, log_event, is_authenticated, validate_cookie, generate_cookie
import configparser
import requests
from tv_functions import tv_shows, get_tv_poster, stream_tv_episode

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('config.cfg')

app = Flask(__name__)


bad_connections = set()
TMDB_BASE_URL = config['DEFAULT']['TMDB_BASE_URL']
TMDB_API_KEY = config['DEFAULT']['API_KEY']
private_key_path = config['DEFAULT']['PRIVATE_KEY_PATH']
certificate_path = config['DEFAULT']['CERTIFICATE_PATH']
check_posters = config['DEFAULT']['CHECK_POSTERS']
check_TV_posters = config['DEFAULT']['CHECK_TV_POSTERS']
create_tables = config['DEFAULT']['CREATE_TABLES']
make_screenshots = config['DEFAULT']['make_screenshots']
srt_vtt = config['DEFAULT']['srt_vtt']
film_directory = config['DEFAULT']['FILMS_FOLDER_PATH']
tv_shows_directory = config['DEFAULT']['TV_FOLDER_PATH']
password_from_config = config['DEFAULT']['PASSWORD']
poster_on_off = eval(config['BOOL']['POSTERS_ON_OFF'])
srt_to_vtt_ON_OFF = eval(config['BOOL']['srt_to_vtt_ON_OFF'])
db_file = config['SECURITY']['DB_FILE']

limiter = Limiter(app)

try:
    if srt_to_vtt_ON_OFF:
        subprocess.run(['py', srt_vtt], check=True)

    if poster_on_off:
        subprocess.run(['py', make_screenshots], check=True)
        subprocess.run(['py', create_tables], check=True)
        subprocess.run(['py', check_posters], check=True)
        subprocess.run(['py', check_TV_posters], check=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")

@app.before_request
def before_request():
    block_bad_connections()

def get_film_list(directory):
    films = []
    for film_folder in os.listdir(directory):
        film_path = os.path.join(directory, film_folder)
        if os.path.isdir(film_path):
            film_info = {'name': film_folder, 'video_file': None, 'poster_path': None, 'banner_path': None, 'subtitle_path': None}

            for file in os.listdir(film_path):
                file_path = os.path.join(film_path, file)
                if os.path.isfile(file_path):
                    if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')) and film_info['video_file'] is None:
                        film_info['video_file'] = file
                    elif file.lower().endswith(('.jpg', '.png', '.jpeg')):
                        if '_banner' in file.lower():
                            film_info['banner_path'] = f"/media/{film_folder}/{file}"
                        else:
                            film_info['poster_path'] = f"/media/{film_folder}/{file}"
                    elif file.lower().endswith(('vtt')):
                        film_info['subtitle_path'] = file

            films.append(film_info)

    return films



@app.route('/API/<path:subpath>', methods=['GET'])
def api_passthrough(subpath):
    url = f"{TMDB_BASE_URL}/{subpath}"
    params = request.args.to_dict()
    params['api_key'] = TMDB_API_KEY

    headers = {
        "Accept": "application/json",
        "Authorization": TMDB_API_KEY
    }
    tmdb_response = requests.get(url, params=params, headers=headers)

    if tmdb_response.status_code == 200:
        return jsonify(tmdb_response.json())
    else:
        return jsonify({"error": f"TMDb API request failed with status code {tmdb_response.status_code}"}), tmdb_response.status_code

@app.route('/tv')
def tv_shows_route():
    return tv_shows(is_authenticated, request, tv_shows_directory)

@app.route('/tv/<show_name>/<file_name>')
def get_tv_poster_route(show_name, file_name):
    return get_tv_poster(is_authenticated, request, tv_shows_directory, show_name, file_name)

@app.route('/tv/<show_name>/<season_name>/<episode_name>')
def stream_tv_episode_route(show_name, season_name, episode_name):
    return stream_tv_episode(is_authenticated, request, tv_shows_directory, show_name, season_name, episode_name)

    
@app.route('/')
def home():
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    print("User authenticated successfully!")
    films = get_film_list(film_directory)
    return make_response(render_template('index.html', films=films))

@app.route('/submit_password', methods=['POST'])
@limiter.limit("5 per minute")
def submit_password():
    password = request.form.get('password')

    if password == password_from_config:
        new_cookie = generate_cookie(db_file)
        response = make_response(redirect(url_for('home')))
        response.set_cookie('auth_cookie', new_cookie, max_age=28800, secure=False, httponly=True)
        return response
    else:
        log_event('Incorrect Password Attempt', f"IP={request.remote_addr}")
        return 'Incorrect password. Please try again.'

@app.route('/media/<film_folder>/')
def stream_media(film_folder):
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    film_path = os.path.join(film_directory, film_folder)

    for file in os.listdir(film_path):
        file_path = os.path.join(film_path, file)
        if os.path.isfile(file_path) and file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            return send_file(file_path)

    abort(404)

@app.route('/media/<film_folder>/<file_name>')
def get_poster(film_folder, file_name):
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    film_path = os.path.join(film_directory, film_folder)
    requested_file_path = os.path.join(film_path, file_name)

    return send_file(requested_file_path) if os.path.isfile(requested_file_path) else abort(404)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(e)
