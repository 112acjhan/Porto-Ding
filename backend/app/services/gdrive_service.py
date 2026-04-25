import io
import mimetypes
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

class GoogleDriveService:
    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        
        self.folder_id = "1k399iaa-U20Xkpb1Mne-MB5-yfojTVnX"

    def upload_file(self, file_name: str, file_bytes: bytes) -> str:
        """Uploads bytes to the specific folder and returns the viewable URL."""
        file_metadata = {
            'name': file_name,
            'parents': [self.folder_id]
        }

        mime_type, _ = mimetypes.guess_type(file_name)

        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=False)
        
        file = self.service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    

test = GoogleDriveService()