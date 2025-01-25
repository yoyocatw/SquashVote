import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def youtube_client():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    api_service_name = "youtube"
    api_version = "v3"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client_secrets_file = os.path.join(BASE_DIR, "client", "client_secret.json")

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube
