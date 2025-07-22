# dagobah_email

**Tools for Gmail thread and message parsing, Gemini formatting, and more.**

---

## Features

- Fetches emails from Gmail using the Gmail API.
- Extracts main text and attachments from emails, including forwarded and nested messages.
- Uses Gemini (Google GenAI) to structure and summarize email threads.
- Outputs structured JSON with metadata, text, and attachments for each message in a thread.

---

## Installation

1. **Clone the repository** and navigate to the project root.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package in editable mode:**
   ```bash
   pip install -e .
   ```

---

## Setup

- **Google API Credentials:**  
  Place your `credentials.json` (from Google Cloud Console) in the project root.
- **Gemini API Key:**  
  Set the `GEMINI_API_KEY` environment variable in your shell or in a `.env` file in the project root:
  ```
  GEMINI_API_KEY=your-gemini-api-key
  ```

---

## Usage

### **From Python**

```python
from dagobah_email import version_2

version_2()
```

This will:
- Fetch the most recent email from your Gmail inbox.
- Extract the main text and attachments.
- Use Gemini to process and structure the email content.
- Print and write the output to `output.txt`.

### **From the Command Line**

You can also run a script that calls `version_2()`:
```bash
python -c "from dagobah_email import version_2; version_2()"
```

---

## API

### **Top-level**

- `version_2()`:  
  Fetches, processes, and summarizes the most recent Gmail message.  
  Output is printed and written to `output.txt`.

### **Submodules**

- `dagobah_email.gemini_formatter.gemini_email_preformatter`
  - `extract_main_text_and_attachments(raw_email)`
  - `summarize_main_text_with_gemini(main_text)`

- `dagobah_email.gmail_fetch.gmail_api_mail_fetch`
  - `fetch_most_recent_email()`

---

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies:
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`
- Gemini API access

---

## Notes

- The first time you run the Gmail fetch, you will be prompted to authenticate and a `token.json` will be created.
- Make sure your environment variables are set before running.
- For advanced usage, you can import and use the lower-level functions/classes directly.

---

## License

MIT License (or specify your license here) 