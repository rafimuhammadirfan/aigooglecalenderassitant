import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def create_service(client_secret_file, api_name, api_version, scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = scopes

    creds = None
    working_dir = os.getcwd()
    token_dir = os.path.join(working_dir, 'token_files')
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)

    token_file = os.path.join(token_dir, f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json')

    # Load token jika sudah ada
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Jika belum ada / expired → refresh atau login ulang
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Simpan token ke file
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
        print(f"{API_SERVICE_NAME} service created successfully")
        return service
    except Exception as e:
        print(f"Error creating service: {e}")
        return None
