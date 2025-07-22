import os
import email
from email import policy
from email.parser import BytesParser

def extract_main_text_and_attachments(raw_email):
    # Parse the raw email into an email.message.Message object
    if isinstance(raw_email, bytes):
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    else:
        msg = email.message_from_string(raw_email, policy=policy.default)
    # Extract plain text body
    text = ""
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                charset = part.get_content_charset() or 'utf-8'
                text += part.get_payload(decode=True).decode(charset, errors='replace')
            elif 'attachment' in content_disposition:
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
    else:
        charset = msg.get_content_charset() or 'utf-8'
        text = msg.get_payload(decode=True).decode(charset, errors='replace')
    return text.strip(), attachments

# This function will only initialize Gemini and call the API if needed
# It operates on the output of extract_main_text_and_attachments

def summarize_main_text_with_gemini(main_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
You are an email parser. Given the following raw email text, extract all messages (including forwarded and quoted messages) and output a structured JSON object with the following format:

{{
  "forwarder_metadata": {{
    "from": ...,
    "to": ...,
    "cc": ...,
    "date": ...,
    "subject": ...,
    "message_id": ...
  }},
  "forwarder_attachments": [ ... ],
  "mails": [
    {{
      "metadata": {{
        "from": ...,
        "to": ...,
        "cc": ...,
        "date": ...,
        "subject": ...,
        "message_id": ...
      }},
      "text_content": "...",
      "attachments": [ ... ]
    }},
    ...
  ]
}}

- Each "mail" in "mails" should correspond to a message in the thread, including forwarded or quoted messages.
- For each message, extract as much metadata as possible (from, to, cc, date, subject, message_id).
- For each message, extract the main text content (excluding quoted replies).
- For each message, list any mentioned or attached filenames in "attachments".
- If a field is missing, use null.
- Do not include any explanation or extra text, only output the JSON.

Here is the email text:
---
{main_text}
---
""",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    return response.text