import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]



# currently gets the most recent email from the user's inbox
# TODO: activate upon new received email event

def fetch_most_recent_email():
    """Fetches the most recent raw email from the user's inbox and returns the raw email bytes."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
        messages = results.get("messages", [])
        if not messages:
            return None
        msg_id = messages[0]["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
        import base64
        raw = base64.urlsafe_b64decode(msg_data["raw"])
        return raw
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
