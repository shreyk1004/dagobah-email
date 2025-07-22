import email
from email import policy
from email.parser import BytesParser
import re
from typing import List, Dict, Any

class Mail:
    def __init__(self, metadata: Dict[str, Any], text_content: str, attachments: List[Dict[str, Any]]):
        self.metadata = metadata
        self.text_content = text_content
        self.attachments = attachments

    def as_dict(self):
        return {
            'metadata': self.metadata,
            'text_content': self.text_content,
            'attachments': self.attachments
        }

class Thread:
    def __init__(self, forwarder_metadata: Dict[str, Any], forwarder_attachments: List[Dict[str, Any]], mails: List[Mail]):
        self.forwarder_metadata = forwarder_metadata
        self.forwarder_attachments = forwarder_attachments
        self.mails = mails

    def as_dict(self):
        return {
            'forwarder_metadata': self.forwarder_metadata,
            'forwarder_attachments': self.forwarder_attachments,
            'mails': [mail.as_dict() for mail in self.mails]
        }

# --- Utility functions ---
def extract_core_content(email_message):
    text = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                charset = part.get_content_charset() or 'utf-8'
                text += part.get_payload(decode=True).decode(charset, errors='replace')
    else:
        charset = email_message.get_content_charset() or 'utf-8'
        text = email_message.get_payload(decode=True).decode(charset, errors='replace')
    return text.strip()

def clean_email_body(core_content):
    return core_content.strip()

def extract_metadata(email_message):
    metadata = {
        'subject': email_message.get('Subject'),
        'from': email_message.get('From'),
        'date': email_message.get('Date'),
        'to': email_message.get('To'),
        'cc': email_message.get('Cc'),
        'bcc': email_message.get('Bcc'),
        'message_id': email_message.get('Message-ID'),
    }
    return metadata

def process_attachments(email_message):
    attachments = []
    for part in email_message.walk():
        content_disposition = str(part.get('Content-Disposition'))
        if 'attachment' in content_disposition:
            filename = part.get_filename()
            payload = part.get_payload(decode=True)
            attachments.append({
                'filename': filename,
                'content_type': part.get_content_type(),
                'size': len(payload) if payload else 0,
            })
    return attachments

def split_inline_thread(text):
    pattern = r'(?:-+ Forwarded message -+)'
    splits = re.split(pattern, text)
    # Remove empty or whitespace-only splits
    messages = [s.strip() for s in splits if s.strip()]
    return messages

def extract_headers_from_text(text):
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    headers = {}
    lines = text.split('\n')
    # Extract headers
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Check for From, Date, Subject as before
        for field in ['From', 'Date', 'Subject']:
            if re.match(rf'^\s*{field}:', line, re.IGNORECASE):
                value = line.split(':', 1)[1].strip()
                headers[field.lower().replace('-', '_')] = value
                break
        # Special handling for To and Cc
        for multi_field in ['To', 'Cc']:
            if re.match(rf'^\s*{multi_field}:', line, re.IGNORECASE):
                value = line.split(':', 1)[1].strip()
                i += 1
                # Collect all subsequent lines containing '>' (email address end)
                while i < n and '>' in lines[i]:
                    value += ' ' + lines[i].strip()
                    i += 1
                headers[multi_field.lower()] = value
                break
        else:
            i += 1
    return headers

# --- Main parsing logic ---
def parse_mail_from_message(email_message) -> Mail:
    metadata = extract_metadata(email_message)
    text_content = clean_email_body(extract_core_content(email_message))
    attachments = process_attachments(email_message)
    return Mail(metadata, text_content, attachments)

def parse_thread_from_raw_email(raw_email_content) -> Thread:
    if isinstance(raw_email_content, bytes):
        email_message = BytesParser(policy=policy.default).parsebytes(raw_email_content)
    else:
        email_message = email.message_from_string(raw_email_content, policy=policy.default)

    forwarder_metadata = extract_metadata(email_message)
    forwarder_attachments = process_attachments(email_message)
    mails = []

    # 1. Extract attached emails (message/rfc822)
    for part in email_message.walk():
        if part.get_content_type() == 'message/rfc822':
            forwarded_msg = part.get_payload(0)
            mails.append(parse_mail_from_message(forwarded_msg))

    # 2. Extract inline/quoted emails
    if not mails:
        text_content = extract_core_content(email_message)
        inline_mails = split_inline_thread(text_content)
        for inline_mail in inline_mails:
            headers = extract_headers_from_text(inline_mail)
            # Remove headers from body (split at first blank line)
            body = re.split(r'\n\s*\n', inline_mail, maxsplit=1)
            body_text = body[1].strip() if len(body) > 1 else ''
            mails.append(Mail(headers, body_text, []))
    else:
        mails.append(parse_mail_from_message(email_message))

    return Thread(forwarder_metadata, forwarder_attachments, mails)