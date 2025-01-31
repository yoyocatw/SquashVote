import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
from django.conf import settings
def youtube_client():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"

    credentials = Credentials(
        None,
        refresh_token= settings.GOOGLE_REFRESH_TOKEN,
        token_uri= settings.GOOGLE_TOKEN_URI,
        client_id= settings.GOOGLE_CLIENT_ID,
        client_secret= settings.GOOGLE_CLIENT_SECRET,
    )
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None 

   

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube



'''
Manual Authentication
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
            flow.redirect_uri = settings.URL 
            credentials = flow.run_local_server()
        with open(token_file, "w") as file:
            file.write(credentials.to_json())
            '''