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
            elif part.get_filename():
                attachments.append(part.get_filename())
    else:
        charset = msg.get_content_charset() or 'utf-8'
        text = msg.get_payload(decode=True).decode(charset, errors='replace')
    return text, attachments

def summarize_main_text_with_gemini(main_text):
    # Only import and initialize Gemini if this function is called
    from google import genai
    from google.genai import types
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)
    # Example prompt, replace with your actual prompt
    prompt = f"""

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

        Email text:
        {main_text}
        """
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt,
                                              config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)))
    return response.text