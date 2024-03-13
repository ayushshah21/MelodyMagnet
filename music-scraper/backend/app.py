from flask import Flask, send_file, Response, redirect, url_for, request
from selenium import webdriver
from chromedriver_py import binary_path # this will get you the path variable
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pytube import YouTube 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from zipfile import ZipFile
from io import BytesIO
from flask_cors import CORS
import shutil  # Import shutil for folder deletion
from dotenv import load_dotenv

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
        # Example API request: Search for videos by a query keyword
        request = youtube.search().list(
            part="id,snippet",
            maxResults=1,
            type='video',
            q=song  # Change your query here
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
    playlist_url = request.args.get('playlist_url')
    if not playlist_url:
        return "No playlist URL provided", 400
    playlistId = playlist_url.split('pl.u-')[1]
    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc)
    # driver.get('https://music.apple.com/us/playlist/run/pl.u-gxblgGltb33krX7')
    driver.get(f'https://music.apple.com/us/playlist/run/{playlist_url}')
    wait_for_page_load(driver)
    # Your scraping logic here
    #songElements = driver.find_elements(By.CLASS_NAME, "songs-list-row__song-name-wrapper svelte-154tqzm")
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
    path = os.path.join('./downloads', playlistId)
    os.mkdir(path)


    for song in songs:
        yt = YouTube(getSongLink(song))
        video = yt.streams.filter(only_audio=True).first()
        # download the file 
        out_file = video.download(output_path=path) 
        
        # save the file 
        new_file = path + '/' + song + '.mp3'
        os.rename(out_file, new_file)
        # Assuming `songs` is your list of song names
        songs_query = ','.join(songs)  # Join list into a string separated by commas
    
        
    return redirect(url_for('download_files', playlistID=playlistId, songs=songs_query))
    
    
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

    # Important: Move the pointer to the beginning of the BytesIO buffer before sending
    zip_buffer.seek(0)

    #Delete playlist subfolder
    # directory.r

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

