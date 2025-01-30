import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

def youtube_client():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client_secrets_file = os.path.join(BASE_DIR, "client", "client_secret.json")
    token_file = os.path.join(BASE_DIR, "client", "token.json")

    credentials = None
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as token:
                credentials = Credentials.from_authorized_user_info(json.load(token), scopes=scopes)
        except:
            print('No token')
            os.remove(token_file)
            credentials = None

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except:
                print('Token refresh failed...')
                credentials = None
        if not credentials:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes)
            flow.redirect_uri = 'http://localhost:8080/'
            credentials = flow.run_local_server()
        with open(token_file, "w") as file:
            file.write(credentials.to_json())

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube
