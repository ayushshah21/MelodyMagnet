from flask import Flask, send_file, Response, redirect, url_for, request
from selenium import webdriver
from chromedriver_py import binary_path 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pytube import YouTube 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from zipfile import ZipFile
from io import BytesIO
from flask_cors import CORS
import shutil  
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
CORS(app)  # Setup CORS
load_dotenv()

@app.after_request
def after_request(response):
    app.logger.info(response.headers)
    return response
@app.route('/test-cors')
def test_cors():
    return "CORS should be enabled for this response."


def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def getSongLink(song):
    api_key = os.environ.get('YOUTUBE_API_KEY')

    
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        request = youtube.search().list(
            part="id,snippet",
            maxResults=1,
            type='video',
            q=song 
        )
        response = request.execute()

        if response['items']:
            top_video_id = response['items'][0]['id']['videoId']
            top_video_link = f'https://www.youtube.com/watch?v={top_video_id}'
            return top_video_link
        else:
            return "No results found."

    except HttpError as e:
        print(f"An HTTP error occurred: {e.resp.status} {e.content}")


@app.route('/', methods=['GET', 'POST'])
def main():
    playlistID = request.args.get('playlist_id')
    playlistName = request.args.get('playlist_name')
    print(playlistID)
    print(playlistName)
    if not playlistID:
        return "No playlist URL provided", 400
    if not playlistName:
        return "No playlist name provided", 400

    # # Set up Chrome options for headless execution
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Enables headless mode
    # chrome_options.add_argument("--no-sandbox")  # Bypasses OS security model
    # chrome_options.add_argument("--disable-dev-shm-usage")  # Addresses limited resource problems

    # # Initialize ChromeService
    # svc = webdriver.ChromeService(executable_path=binary_path)
    # # Create a WebDriver instance with the specified service and options
    # driver = webdriver.Chrome(service=svc, options=chrome_options)


    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc)


    driver.get(f'https://music.apple.com/us/playlist/{playlistName}/pl.u-{playlistID}')
    wait_for_page_load(driver)
    JS = '''
        let songs = [];
        let songElements = document.getElementsByClassName("songs-list-row__song-name-wrapper svelte-154tqzm");
        for (let i = 0; i < songElements.length; i++) {
            songs.push(songElements[i].innerText);
        }
        console.log('Songs count:', songs.length);
        return songs;  // Returning the length for capturing it in Python'''
    songs = driver.execute_script(JS)
    driver.quit()
    path = os.path.join('./downloads', playlistID)
    os.mkdir(path)


    for song in songs:
        yt = YouTube(getSongLink(song))
        video = yt.streams.filter(only_audio=True).first()
        # download the file 
        out_file = video.download(output_path=path) 
        
        # save the file 
        new_file = path + '/' + song + '.mp3'
        os.rename(out_file, new_file)
        songs_query = ','.join(songs)  # Join list into a string separated by commas
    
        
    return redirect(url_for('download_files', playlistID=playlistID, songs=songs_query))
    
    
@app.route('/downloads/<playlistID>')
def download_files(playlistID):
    print(f"Download files called with playlistID: {playlistID}")
    songs_query = request.args.get('songs', '')
    print(f"Songs query: {songs_query}")
    songs = songs_query.split(',') if songs_query else []
    print(f"Songs list: {songs}")
    appendSuffix = ".mp3"
    modified_list = [item + appendSuffix for item in songs]
    directory = os.path.join('./downloads', playlistID)
    # Create a byte stream buffer to hold the ZIP file
    zip_buffer = BytesIO()

    # Create a ZIP file in the byte stream buffer
    with ZipFile(zip_buffer, 'w') as zip_file:
        for song in modified_list:
            # Create a secure path to prevent directory traversal attacks
            secure_path = os.path.join(directory, os.path.basename(song))
            # Add file to the ZIP file
            zip_file.write(secure_path, arcname=os.path.basename(song))

    # Move the pointer to the beginning of the BytesIO buffer before sending
    zip_buffer.seek(0)


    # Send the ZIP file to the client
    return Response(zip_buffer.getvalue(), mimetype='application/zip', headers={'Content-Disposition': 'attachment;filename=songs.zip'})

@app.route('/cleanup/<playlistID>')
def cleanup(playlistID):
    directory = os.path.join('./downloads', playlistID)
    try:
        shutil.rmtree(directory)  # This deletes the directory and all its contents
        return "Cleanup successful", 200
    except Exception as e:
        return f"Error during cleanup: {str(e)}", 500
    

if __name__ == '__main__':
    app.run(debug=True)

