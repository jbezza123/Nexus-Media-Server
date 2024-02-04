from flask import jsonify, make_response, render_template, send_file, abort
import os
import requests
from security import is_authenticated
import configparser

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('config.cfg')

db_file = config['SECURITY']['DB_FILE']

def get_tv_show_list(directory):
    tv_shows = []
    if not os.path.exists(directory):
        os.makedirs(directory)

    for show_folder in os.listdir(directory):
        show_path = os.path.join(directory, show_folder)
        if os.path.isdir(show_path):
            show_info = {'name': show_folder, 'poster_path': None, 'seasons': []}

            for file in os.listdir(show_path):
                file_path = os.path.join(show_path, file)
                if os.path.isfile(file_path) and file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    show_info['poster_path'] = f"{show_folder}/{file}"
                    break

            for season_folder in os.listdir(show_path):
                season_path = os.path.join(show_path, season_folder)
                if os.path.isdir(season_path):
                    show_info['seasons'].append({'name': season_folder, 'episodes': [f for f in os.listdir(season_path) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]})

            tv_shows.append(show_info)

    return tv_shows

def tv_shows(is_authenticated, request, tv_shows_directory):
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    print("User authenticated successfully!")
    tv_shows = get_tv_show_list(tv_shows_directory)
    return make_response(render_template('tv_shows.html', tv_shows=tv_shows))

def get_tv_poster(is_authenticated, request, tv_shows_directory, show_name, file_name):
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    show_path = os.path.join(tv_shows_directory, show_name)
    requested_file_path = os.path.join(show_path, file_name)

    return send_file(requested_file_path) if os.path.isfile(requested_file_path) else abort(404)

def stream_tv_episode(is_authenticated, request, tv_shows_directory, show_name, season_name, episode_name):
    if not is_authenticated(request, db_file):
        return make_response(render_template('captive_portal.html'))
    show_path = os.path.join(tv_shows_directory, show_name, season_name)
    episode_path = os.path.join(show_path, episode_name)

    if 'mkv' in episode_name:
        return send_file(episode_path, mimetype='video/x-matroska', as_attachment=False) if os.path.isfile(episode_path) else abort(404)
    elif 'mp4' in episode_name:
        return send_file(episode_path, mimetype='video/mp4', as_attachment=False) if os.path.isfile(episode_path) else abort(404)
