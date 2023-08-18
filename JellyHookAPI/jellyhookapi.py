#!/usr/bin/env python3

from flask import Flask, request, jsonify
# import urllib.request
import requests
import tempfile
import io
import re

# global variables
TMDB_API_KEY = "TMDB_API_KEY"
LANGUAGE = "fr-FR"
LANGUAGE2 = "en-US"
base_url = "https://api.themoviedb.org/3"

app = Flask(__name__)

# function to send to whatsapp API
def send_whatsapp(title, overview, imdb, tmdb, vidt, picture_path):
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
    else:
        caption += f'```{get_synopsis(vidt)}```\n'
    #caption += f'_Watch here:{watch_link}_\n'
    # if imdb not empty, add it to the caption
    if imdb:
        caption += f'• IMDb: {shorten_link(imdb)}\n'
    # if tmdb not empty, add it to the caption
    if tmdb:
        caption += f'• TMDb: {shorten_link(tmdb)}\n'
    # get the shortened youtube trailer link from tmdb API
    #trailer_links = get_trailer_link(vidt)
    caption += get_trailer_link(vidt)
    # add the trailer link to the caption
    #caption += f'• Trailer FR: {trailer_links[0]}\n • Trailer EN: {trailer_links[1]}'

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

# function to get the synopsis of the video from tmdb API
def get_synopsis(vidt):
    # parameters
    global TMDB_API_KEY
    global LANGUAGE
    global LANGUAGE2
    global base_url

    languages = [LANGUAGE, LANGUAGE2]

    for language in languages:
        if vidt:
            url = f"{base_url}/{vidt}?api_key={TMDB_API_KEY}&language={language}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()["overview"]

    return None # synopsis not found

# function to get the shortened youtube trailer link from tmdb API
def get_trailer_link(vidt):
    # parameters
    global TMDB_API_KEY
    global LANGUAGE
    global LANGUAGE2
    global base_url

    # regex to search trailer depending on the language
    languages = [(LANGUAGE,r"bande[-\s]?annonce"), (LANGUAGE2,r"trailer")]
    trailer_links = []

    # search for the corresponding trailer depending on the language
    for language, pattern in languages:
        if vidt:
            youtube_key = search_trailer_key(vidt, language, pattern)
            if youtube_key:
                trailer_links.append(f"https://youtu.be/{youtube_key}")

    if trailer_links:
        if len(trailer_links) == 2:
            return f"• Trailer FR: {trailer_links[0]}\n • Trailer EN: {trailer_links[1]}"
        elif len(trailer_links) == 1:
            return f"• Trailer: {trailer_links[0]}\n"
        else:
            return "Aucune bande-annonce trouvée"
    else:
        return "Aucune bande-annonce trouvée"

    #return "Aucune bande-annonce trouvée" if not trailer_links else trailer_links

# function to search for the trailer key in the tmdb API
def search_trailer_key(vidt, language, pattern):
    # parameters
    global TMDB_API_KEY
    global base_url

    # search for the corresponding trailer depending on the language
    url = f"{base_url}/{vidt}/videos?api_key={TMDB_API_KEY}&language={language}"

    response = requests.get(url, timeout=10)

    # check if the request was successful
    if response.status_code != 200:
        return None

    # parse the response JSON
    results = response.json()["results"]

    # search for the trailer key in the results
    for video in results:
        if re.search(pattern, video["name"], flags=re.IGNORECASE):
            return video["key"]

    return None # trailer key not found

# function to get the poster url from tmdb API
def get_tmdb_poster_url(vidt):
    global TMDB_API_KEY
    global base_url

    # poster url
    tmdb_url = f"{base_url}/{vidt}/images?api_key={TMDB_API_KEY}"

    # request to the TMDB API
    response = requests.get(tmdb_url, timeout=10)

    # check if the request was successful
    if response.status_code != 200:
        raise ValueError('The request to the TMDb API was not successful.')

    # parse the response JSON
    results = response.json()

    # get the poster url
    poster_url = results["posters"][0]["file_path"]

    # return the poster url
    return poster_url

# function to shorten links
def shorten_link(link):
    # find domain name in the link
    domain = link.split("//")[1].split("/")[0]

    if domain == "www.themoviedb.org":
        # replace useless part of the link for TMDb
        return link.replace("https://www.themoviedb.org/", "https://tmdb.org/")
    elif domain == "www.imdb.com":
        # replace useless part of the link for IMDb
        return link.replace("https://www.imdb.com/", "https://imdb.com/")
    else:
        # return the link if domain name not recognize
        return link

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

    # get tmdb video type, movie or tv, and id from the given tmdb link
    # Split the link by "/" to extract the parts
    parts = tmdb.split("/")
    # Find the index of "tv" or "movie" in the parts list
    type_index = parts.index("tv") if "tv" in parts else parts.index("movie")
    # The type (tv or movie) will be the element after the type_index
    video_type = parts[type_index]
    # Extract the ID from the link
    idt = parts[-1]
    # Remove extra text from ID, if any
    if "-" in idt:
        idt = idt.split("-")[0]
    # Check ID is numeric
    if not idt.isdigit():
        raise ValueError('The given TMDb link is not valid.')
    vidt = f"{video_type}/{idt}"

    if picture_url == '':
        try:
            picture_url = get_tmdb_poster_url(vidt)
        except ValueError:
            # if the poster url is not found, use the default one
            picture_url = "./default-poster.png"

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
        send_whatsapp(title, overview, imdb, tmdb, vidt, temp.name)
        # remove the temporary file (if: NamedTemporaryFile(delete=False))
        #os.remove(temp.name)

    return jsonify({'message': 'Data received successfully!'})

if __name__ == '__main__':
    # run the app in debug mode with specified host and port
    app.run(debug=True, host='0.0.0.0', port=7777)
