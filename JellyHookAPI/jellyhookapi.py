#!/usr/bin/env python3

from flask import Flask, request, jsonify
# import urllib.request
import requests
import tempfile
import io

app = Flask(__name__)

# function to send to whatsapp API
def send_whatsapp(title, overview, imdb, tmdb, picture_path):
    # Parameters
    phone = "<phone-number>@s.whatsapp.net"
    # phone = "<group-number>@g.us" # group
    # whatsapp internal docker subnet ip
    url = "http://10.10.66.200:3000/send/image"
    # whatsapp API basic http auth 'username','password'
    auth = ("johnsmith","S3cR3t!")
    view_once = "False"
    compress = "True"

    # Set the headers
    headers = {'accept': 'application/json'}

    # Set the caption
    # as if title does not exist, it will be empty string, so it will not be added to the caption
    caption = f'*{title}*\n'
    # if overview not empty, add it to the caption
    if overview:
        caption += f'```{overview}```\n'
    #caption += f'_Watch here:{watch_link}_\n'
    # if imdb not empty, add it to the caption
    if imdb:
        caption += f'• IMDb: {imdb}\n'
    # if tmdb not empty, add it to the caption
    if tmdb:
        caption += f'• TMDb: {tmdb}\n'
    # get the shortened youtube trailer link from tmdb API
    trailer_link = get_trailer_link(tmdb)
    # add the trailer link to the caption
    if trailer_link:
        caption += f'• Trailer: {trailer_link}\n'

    # Set the data
    data = {
        'phone': phone,
        'caption': caption,
        'view_once': view_once,
        'compress': compress
    }

    # Set the files
    with open(picture_path, 'rb') as f:
        # read the content of the file
        file_content = f.read()
    
        # Use io.BytesIO to create a temporary file object containing the file contents
        file_data = io.BytesIO(file_content)
    
        # Add the file to the request
        files = {'image': ('image', file_data, 'image/png')}
    
    # Make the request
    response = requests.post(url, headers=headers, data=data, auth=auth, files=files)

    # return the responses
    return response

# function to get the shortened youtube trailer link from tmdb API
def get_trailer_link(tmdb):
    # Parameters
    TMDB_API_KEY = "TMDB_API_KEY"
    LANGUAGE = "fr-FR"

    # base url of the tmdb API
    base_url = "https://api.themoviedb.org/3/"

    # check if the id is a movie or a tv show
    url = f"{base_url}/movie/{tmdb}?api_key={TMDB_API_KEY}&language={LANGUAGE}"
    response = requests.get(url)
    if response.status_code == 200:
        video_type = "movie"
    else:
        url = f"{base_url}/tv/{tmdb}?api_key={TMDB_API_KEY}&language={LANGUAGE}"
        response = requests.get(url)
        if response.status_code == 200:
            video_type = "tv"
        else:
            return None  # the id was not found
        
    # search for the corresponding trailer
    url = f"{base_url}/{video_type}/{tmdb}/videos?api_key={TMDB_API_KEY}&language={LANGUAGE}"
    response = requests.get(url)
    if response.status_code != 200:
        return None  # no trailer was found

    # get all the data of the trailer
    results = response.json().get("results")
    if not results:
        return None  # no trailer was found
    
    # get the key of the trailer
    for video in results:
        if "bande annonce" in video.get("name", "").lower():        
            youtube_key = video.get("key")
            if youtube_key:
                return f"https://youtu.be/{youtube_key}"
    # no trailer found, return the first link
    if not youtube_key and len(results) > 0:
        youtube_key = results[0].get("key")
        if youtube_key:
            # return the shortened youtube link
            return f"https://youtu.be/{youtube_key}"

    return None  # no trailer was found

@app.route('/api', methods=['POST'])
def receive_data():
    # first, check if data header is json
    # the data must be sent with the header 'Content-Type: application/json'
    if not request.is_json:
        return jsonify({'message': 'Data is not json!'}), 400

    data = request.json
    title = data.get('title', '')   # get the value of the key 'title' or return '' if the key doesn't exist
    overview = data.get('overview', '')
    watch_link = data.get('watch_link', '')
    imdb = data.get('imdb', '')
    tmdb = data.get('tmdb', '')
    picture_url = data.get('picture_url', '')
    server_name = data.get('server_name','')

    # download the picture in a temporary file (and don't delete it)
    #with tempfile.NamedTemporaryFile(delete=False) as temp:
    with tempfile.NamedTemporaryFile() as temp:
        # using urllib
        #urllib.request.urlretrieve(picture_url, temp.name)
        # download the picture
        response = requests.get(picture_url)
        temp.write(response.content)
        # DEBUG: print the path of the temporary file
        #print('picture_path: ', temp.name)
        # call the function to send to whatsapp API
        send_whatsapp(title, overview, imdb, tmdb, temp.name)
        # remove the temporary file (if: NamedTemporaryFile(delete=False))
        #os.remove(temp.name)

    return jsonify({'message': 'Data received successfully!'})

if __name__ == '__main__':
    # run the app in debug mode with specified host and port
    app.run(debug=True, host='0.0.0.0', port=7777)
