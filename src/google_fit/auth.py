import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define OAuth 2.0 scopes required for Google Fit
SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]

# Path to the credentials JSON file you downloaded from Google Cloud
CREDENTIALS_FILE = "path/to/your/client_secret.json"
TOKEN_FILE = "token.json"

def authenticate_google_fit():
    creds = None

    # Load saved token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, perform authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds

# Authenticate and get API client
creds = authenticate_google_fit()
service = build("fitness", "v1", credentials=creds)
