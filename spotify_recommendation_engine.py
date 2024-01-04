import base64
import json
import os
from requests import post,get

ClientId = os.environ['Client_ID']
ClientSecret = os.environ['Client_Secret']

def get_token():
  auth_string = ClientId + ':' + ClientSecret
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  url = "https://accounts.spotify.com/api/token"
  headers = {
    "Authorization" : "Basic " + auth_base64,
    "Content-Type" : "application/x-www-form-urlencoded"
  }
  data = {"grant_type" : "client_credentials"}
  result = post(url,headers=headers,data=data)
  result = json.loads(result.content)
  token = result["access_token"]
  return token

def track_to_artistid(token,track_name):
  url = "https://api.spotify.com/v1/search?"
  query = f"q={track_name}&type=track&market=IN&limit=1"
  headers = {"Authorization": "Bearer " + token}
  result = get(url+query,headers=headers)
  result = json.loads(result.content)
  return result["tracks"]["items"][0]["artists"][0]["id"]
  

def artistid_to_genres(token,artistid):
  url = f"https://api.spotify.com/v1/artists/{artistid}"
  headers = {"Authorization": "Bearer " + token}
  result = get(url,headers=headers)
  result = json.loads(result.content)
  return result["genres"]

def track_to_trackid(token,track_name):
  url = "https://api.spotify.com/v1/search?"
  query = f"q={track_name}&type=track&market=IN&limit=1"
  headers = {"Authorization": "Bearer " + token}
  result = get(url+query,headers=headers)
  result = json.loads(result.content)
  return result["tracks"]["items"][0]["id"]

def get_recommendations(token,track_name):
  artistid = track_to_artistid(token,track_name)
  genres = (", ".join(map(str, artistid_to_genres(token,artistid))))
  trackid = (track_to_trackid(token,track_name))
  
  url = "https://api.spotify.com/v1/recommendations?"
  query = f"limit=1&market=IN&seed_artists={artistid}&seed_genres={genres}&seed_tracks={trackid}"
  headers = {"Authorization": "Bearer " + token}
  result = get(url+query,headers=headers)
  result = json.loads(result.content)
  return result["tracks"][0]["name"] + " by "+ result["tracks"][0]["artists"][0]["name"]

#token = get_token()

# print(get_recommendations(token,"Blinding lights"))
#print(track_to_artistid(token,"sugarcrash"))



  