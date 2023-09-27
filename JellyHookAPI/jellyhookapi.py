#!/usr/bin/env python3

from flask import Flask, request, jsonify
import requests
import tempfile
import io
import re

# global variables
TMDB_API_KEY = "TMDB_API_KEY"
LANGUAGE = "fr-FR"
LANGUAGE2 = "en-US"
base_url = "https://api.themoviedb.org/3"
WHATSAPP_API_URL = "http://10.10.66.200:3000" # internal docker subnet ip
WHATSAPP_NUMBER = "<phone-number>@s.whatsapp.net" # Or for a group: "<group-number>@g.us"
WHATSAPP_API_USERNAME = "johnsmith"
WHATSAPP_API_PWD = "S3cR3t!"

app = Flask(__name__)

# function to send to whatsapp API
def send_whatsapp(phone, message, send_image=False, picture_path=None):
    # WhatsApp API Parameters
    url = f"{WHATSAPP_API_URL}/send/image" if send_image else f"{WHATSAPP_API_URL}/send/message"
    auth = (WHATSAPP_API_USERNAME, WHATSAPP_API_PWD)

    # WhatsApp API Headers
    headers = {'accept': 'application/json'}

    # WhatsApp API Data
    data = {'phone': phone}

    if send_image:
        # Send Image
        data['caption'] = message
        data['compress'] = "True"
        files = {'image': ('image', open(picture_path, 'rb'), 'image/png')}
    else:
        # Send Message
        data['message'] = message

    # Send the message to WhatsApp API
    response = requests.post(url, headers=headers, data=data, auth=auth, files=files if send_image else None)
    return response

def format_message(title, overview, imdb, tmdb, vidt, send_image=True):
    message = f'*{title}*\n'

    if overview:
        message += f'```{overview}```\n'
    else:
        message += f'```{get_synopsis(vidt)}```\n'

    if imdb:
        message += f'• IMDb: {shorten_link(imdb)}\n'

    if tmdb:
        message += f'• TMDb: {shorten_link(tmdb)}\n'

    message += get_trailer_link(vidt)

    return message

def is_episode_added(title):
    # Check if the title matches the format "Episode added • ...  SXYZEXYZ ... - Épisode XYZ..."
    match = re.search(r'(Episode added • .+?) - Épisode \d+', title)

    if match:
        new_title = match.group(1)
        return True, new_title
    else:
        return False, title

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

# function to search for the trailer key in the tmdb API
def search_trailer_key(vidt, language, pattern):
    # parameters
    global TMDB_API_KEY
    global base_url

    regex = re.compile(r"^[a-z]+/[0-9]+")
    if "season" in vidt:
        vidt = regex.findall(vidt)[0]

    # search for the corresponding trailer depending on the language
    url = f"{base_url}/{vidt}/videos"
    params = {
        'api_key': TMDB_API_KEY,
        'language': language,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            for video in results:
                if re.search(pattern, video.get("name", ""), flags=re.IGNORECASE):
                    return video.get("key")

    except requests.exceptions.RequestException as e:
        print(f"search_trailer_key request error: {e}")

    return None # trailer key not found

# function to get the poster url from tmdb API
def get_tmdb_poster_url(vidt):
    global TMDB_API_KEY
    global base_url
    global LANGUAGE

    regex = re.compile(r"^[a-z]+/[0-9]+")
    if "season" in vidt:
        vidt = regex.findall(vidt)[0]

    # poster api url
    tmdb_url = f"{base_url}/{vidt}/images?api_key={TMDB_API_KEY}&language={LANGUAGE[:-3]}"

    try:
        # request to the TMDB API
        response = requests.get(tmdb_url, timeout=10)
        # check if the request was successful
        response.raise_for_status()
        # parse the response JSON
        results = response.json()

        # get the first poster url
        if 'posters' in results and len(results['posters']) > 0:
            poster_url = results['posters'][0]['file_path']
            full_poster_url = f"https://image.tmdb.org/t/p/w342{poster_url}"
            return full_poster_url

        # try with other language
        tmdb_url2 = f"{base_url}/{vidt}/images?api_key={TMDB_API_KEY}"
        response = requests.get(tmdb_url2, timeout=10)
        response.raise_for_status()
        results = response.json()
        if 'posters' in results and len(results['posters']) > 0:
            poster_url = results['posters'][0]['file_path']
            full_poster_url = f"https://image.tmdb.org/t/p/w342{poster_url}"
            return full_poster_url
        else:
            return jsonify({'message': 'No poster found'}), 400

    except requests.exceptions.RequestException as req_err:
        return jsonify({'message': f'get poster: Request error: {str(req_err)}'}), 400
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'message': f'get poster: HTTP error: {str(http_err)}'}), 400
    except KeyError as key_err:
        return jsonify({'message': f'get poster: Key not found: {str(key_err)}'}), 400
    except IndexError as index_err:
        return jsonify({'message': f'get poster: Index out of bounds: {str(index_err)}'}), 400
    except Exception as e:
        return jsonify({'message': f'get poster: Another error occurred: {str(e)}'}), 400

def imdb_to_tmdb(imdb_id):
    # get tmdb id from imdb id
    global TMDB_API_KEY
    global LANGUAGE
    global base_url

    url = f"{base_url}/find/{imdb_id}?external_source=imdb_id&language={LANGUAGE}&api_key={TMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        results = response.json()

        if "movie_results" in results and results["movie_results"]:
            vidt = f"movie/{results['movie_results'][0]['id']}"
            tmdb_link = f"https://tmdb.org/{vidt}"
            return vidt, tmdb_link
        elif "tv_results" in results and results["tv_results"]:
            vidt = f"tv/{results['tv_results'][0]['id']}"
            tmdb_link = f"https://tmdb.org/{vidt}"
            return vidt, tmdb_link
        elif "tv_episode_results" in results and results["tv_episode_results"]:
                tmdb_link = f"https://tmdb.org/tv/episode/{results['tv_episode_results'][0]['id']}"
                show_id = results['tv_episode_results'][0]['show_id']
                season_nb = results['tv_episode_results'][0]['season_number']
                episode_nb = results['tv_episode_results'][0]['episode_number']
                vidt =  f"tv/{show_id}/season/{season_nb}/episode/{episode_nb}"
                return vidt, tmdb_link
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None, None

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

def parse_tmdb_link(tmdb):
    # TMDb link example: "https://tmdb.org/movie/12345"
    tmdb = tmdb.rstrip('/')
    parts = tmdb.split("/")
    if len(parts) >= 4 and (parts[-2] == "movie" or parts[-2] == "tv"):
        video_type = parts[-2]
        video_id = parts[-1]
        return f"{video_type}/{video_id}"
    return None

def parse_imdb_link(imdb):
    # IMDb link example: "https://www.imdb.com/title/tt1234567/"
    imdb = imdb.rstrip('/')
    parts = imdb.split("/")
    if len(parts) >= 5 and parts[3] == "title":
        imdb_id = parts[4]
        # get video_type, tmdb_id and tmdb link from imdb id
        vidt, tmdb = imdb_to_tmdb(imdb_id)
        if vidt and tmdb:
            return vidt, tmdb
    return None

@app.route('/api', methods=['POST'])
def receive_data():
    if not request.is_json:
        return jsonify({'message': 'Data is not json!'}), 400

    data = request.json
    title = data.get('title', '')
    overview = data.get('overview', '')
    #watch_link = data.get('watch_link', '')
    imdb = data.get('imdb', '')
    tmdb = data.get('tmdb', '')
    picture_url = data.get('picture_url', '')
    #server_name = data.get('server_name', '')

    vidt = ""   # {video_type}/{video_id}
    send_image = True  # Default behavior is to send an image

    if "Season added" not in title:
        if tmdb:
            # Handle TMDb link
            vidt = parse_tmdb_link(tmdb)
        elif imdb:
            # Handle IMDb link
            vidt, tmdb = parse_imdb_link(imdb)

        if vidt is None and imdb:
            vidt, tmdb = parse_imdb_link(imdb)

        if not vidt:
            return jsonify({'message': 'Invalid/empty TMDB or IMDb link!'}), 400

        is_episode, title = is_episode_added(title)
        if is_episode:
            # If it's an episode added message, do not send an image
            send_image = False

        message = format_message(title, overview, imdb, tmdb, vidt, send_image)
    else:
        send_image = False
        message = f'*{title}*'

    if send_image:
        # Use a default image URL if none is provided
        if not picture_url:
            try:
                picture_url = get_tmdb_poster_url(vidt)
            except ValueError:
                # Use a default image URL if the poster is not found
                picture_url = "./default-poster.png"

        with tempfile.NamedTemporaryFile() as temp:
            response = requests.get(picture_url)
            temp.write(response.content)
            send_whatsapp(WHATSAPP_NUMBER, message, send_image, temp.name)
    else:
        send_whatsapp(WHATSAPP_NUMBER, message)
        
    return jsonify({'message': 'Data received successfully!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777)
