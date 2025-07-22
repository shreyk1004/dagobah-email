import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from main import SCOPES


# --- Version 1 ---
# Tries regex splitting the email body to extract the forwarded emails
def version_1():
    """Fetches the most recent message in the user's inbox, processes it as a Thread, and prints the extracted data.
    Also writes the entire output to a txt file.
    """
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
        # Fetch the most recent message ID from the inbox
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=1).execute()
        messages = results.get("messages", [])
        if not messages:
            print("No messages found.")
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write("No messages found.\n")
            return
        output_lines = []
        output_lines.append("Fetching and processing the most recent message...")
        print("Fetching and processing the most recent message...")
        msg_id = messages[0]["id"]
        msg_data = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
        import base64
        raw = base64.urlsafe_b64decode(msg_data["raw"])
        # Process the single email as a Thread
        from email_preformatter import parse_thread_from_raw_email
        thread = parse_thread_from_raw_email(raw)

        # testing purposes #########################################################
        raw_decoded = raw.decode(errors="replace")
        output_lines.append(raw_decoded)
        print(raw_decoded)
        output_lines.append("#####")
        print("#####")
        ############################################################################

        thread_json = json.dumps(thread.as_dict(), indent=2, ensure_ascii=False)
        output_lines.append(thread_json)
        print(thread_json)

        # Write all output to a txt file
        with open("output.txt", "w", encoding="utf-8") as f:
            for line in output_lines:
                f.write(f"{line}\n")

    except HttpError as error:
        print(f"An error occurred: {error}")
        
        # Write all output to a txt file
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(f"An error occurred: {error}\n")

