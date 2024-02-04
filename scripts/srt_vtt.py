import os
import shutil
from pathlib import Path
import configparser
import logging

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('../config.cfg')

film_directory = config['DEFAULT']['FILMS_FOLDER_PATH']
logs_directory = config['DEFAULT']['LOGS_DIRECTORY']

log_file_path = os.path.join(logs_directory, 'conversion.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def convert_srt_to_webvtt(srt_path, webvtt_path):
    try:
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()

        # Convert to WebVTT format
        webvtt_content = "WEBVTT\n\n" + srt_content.replace(',', '.')

        with open(webvtt_path, 'w', encoding='utf-8') as webvtt_file:
            webvtt_file.write(webvtt_content)

    except Exception as e:
        logging.error(f"Error converting {srt_path} to WebVTT: {str(e)}")


def copy_srt_to_webvtt(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.srt'):
                srt_path = os.path.join(root, file)
                webvtt_filename = Path(file).stem + '.vtt'
                webvtt_path = os.path.join(root, webvtt_filename)

                # Check if WebVTT file already exists
                if not os.path.exists(webvtt_path):
                    try:
                        # Convert and copy to the same directory
                        convert_srt_to_webvtt(srt_path, webvtt_path)
                        logging.info(f"Converted {srt_path} to {webvtt_path}")

                    except Exception as e:
                        logging.error(f"Error processing {srt_path}: {str(e)}")
                else:
                    logging.info(f"Skipping conversion for {srt_path}. WebVTT file already exists.")

if __name__ == "__main__":
    print('Converting Subtitles!')
    copy_srt_to_webvtt(film_directory)
    print("Conversion and copying completed.")

    # Update the srt_to_vtt_ON_OFF boolean at the end of the script
    config.set('BOOL', 'srt_to_vtt_ON_OFF', 'False')
    with open('config.cfg', 'w') as configfile:
        config.write(configfile)
