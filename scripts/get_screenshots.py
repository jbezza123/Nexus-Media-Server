import os
import cv2
import configparser
import threading

# Load configuration from config.cfg
config = configparser.ConfigParser()
config.read('../config.cfg')

tv_folder = config['DEFAULT']['TV_FOLDER_PATH']
error = []
def capture_screenshot(video_path, output_path):
    #screenshot_path = os.path.join(output_path, os.path.splitext(os.path.basename(video_path))[0] + '.jpg')
    screenshot_path = os.path.join(output_path, os.path.basename(video_path) + '.jpg')

    if os.path.exists(screenshot_path):
        print(f'Screenshot already exists for {video_path}')
        return

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target_frame = total_frames // 2

    try:
        if cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame):
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (1280, 720))
                cv2.imwrite(screenshot_path, frame)
            else:
                print(f'Error capturing screenshot for {video_path}')
    except Exception as e:
        print(f'Error processing video {video_path}: {str(e)}')

    cap.release()


def capture_screenshots_for_tv_shows(tv_folder):
    threads = []

    for show_folder in os.listdir(tv_folder):
        show_path = os.path.join(tv_folder, show_folder)

        if os.path.isdir(show_path):
            for season_folder in os.listdir(show_path):
                season_path = os.path.join(show_path, season_folder)

                if os.path.isdir(season_path):
                    for video_file in os.listdir(season_path):
                        video_path = os.path.join(season_path, video_file)

                        if os.path.isfile(video_path) and video_path.lower().endswith(('.mkv', '.mp4', '.avi')):
                            thread = threading.Thread(target=capture_screenshot, args=(video_path, season_path))
                            threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

# Call the function to capture screenshots for TV shows
capture_screenshots_for_tv_shows(tv_folder)
