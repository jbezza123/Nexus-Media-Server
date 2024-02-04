# Nexus Media Server

Nexus Media Server is a Flask-based media server that allows you to list and organize your film and TV show collections. It includes features such as film popups with cast information, subtitles, and TV show season and episode browsing. Please note that this project is intended for educational purposes, and users are encouraged to own the media legally.

Films should be structured as
- Films/
    - Film_name (Date)/
        - Film.mp4
Tv should be
- TV/
    - Show Name (Date)/
        - Season 1
          - Episode.mp4
          - Episode.mp4
## Getting Started

### Prerequisites

- Python 3.x
- Flask
- [TMDb API Key](https://www.themoviedb.org/settings/api) (Replace `TMDB_AUTH_HERE` in the config file)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Nexus-Media-Server.git
    cd Nexus-Media-Server
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure the server:**

    Edit the `config.cfg` file to set your TMDb API key and other configuration parameters.

    ```ini
    [DEFAULT]
    api_key = Bearer YOUR_TMDB_API_KEY
    password = YOUR_PASSWORD_OF_CHOICE
    ```

4. **Run the server:**

    ```bash
    python app.py
    ```

    Visit `http://localhost:5000` in your browser to access Nexus Media Server.
    localhost may not allow you to log in so use your local ip instead.

## Features

- Film and TV show browsing
- Film popups with cast information
- Subtitles support
- TV show season and episode browsing

## Work in Progress

This project is still under development, and there are several enhancements planned:

- Mobile-friendly templates
- Adding YouTube trailer links to film popups
- User Accounts and Authentication
- Search and Filtering for Tv_shows (Films already has)
- Custom Playlists
- Transcoding (only plays mp4)
- Continuous Playback
- Room Creation
- Invite Friends
- Chat and Communication
- User Avatars
- Room Management
- Emote Reactions

## Acknowledgments

- Thanks to [The Movie Database (TMDb)](https://www.themoviedb.org/) for providing the API used in this project.

## Legal Disclaimer

Please ensure that you legally own the media you access through Nexus Media Server. This project is intended for educational purposes only.
