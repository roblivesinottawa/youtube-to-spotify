"""
log into youtube,
grab liked videos,
create new playlist,
search for song,
add this song to playlist

"""

# all the required imports
import json
import requests
import os
from secrets import spotify_user_id, spotify_token

from requests.api import request
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl


# class that will hold all the methods that follow the steps specified above

class createPlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info={

        }


    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


        return youtube_client
    
    def get_liked_videos(self):
        requests = self.youtube_client.videos().list(
            part="snippet,contentDetails, statistics",
            myRating="like"
        )

        response = request.execute()

        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.co/watch?v={}".format(item["id"])


        # use yputube dl to get song name and artist
        video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)

        song_name = video["track"]
        artist = video["artist"]

        # save important info
        self.all_song_info[video_title]={
            "youtube_url": youtube_url,
            "song_name": song_name,
            "artist": artist,

            # add the uri

            "spotify_uri": self.get_spotify_uri(song_name, artist)
        }
    
    
    def create_playlist(self):
        request_body = json.dumps({
            "name": "youtube liked vids",
            "description": "All liked youtube videos",
            "public": True,

        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        return response_json["id"]


    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/artists/1vCWHaC5f2uS3yhpwWbIA6/albums?album_type=SINGLE&offset=20&limit=10".format(
            song_name,
            artist,
        )

        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()

        songs = response_json['tracks']['items']

        # use first song
        uri = songs[0]["uri"]

        return uri

    def add_song_to_playlist(self):
        # populate songs dictionary
        self.get_liked_videos()

        # collect all uri
        uri = []
        for song, info in self.all_song_info.items():
            uri.append(info["spotify_uri"])

        # create a new playlist
        playlist_id = self.create_playlist()
        
        # add al songs into playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/plyalists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_data,
             headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }

        )

        response_json = response.json()
        return response_json



   
