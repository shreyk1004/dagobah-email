import json

from dagobah_email.gemini_formatter.gemini_email_preformatter import extract_main_text_and_attachments, summarize_main_text_with_gemini
from dagobah_email.gmail_fetch.gmail_api_mail_fetch import fetch_most_recent_email

def version_2():
    """Fetches the most recent message in the user's inbox, extracts main text and attachments, sends to Gemini, and prints/writes the structured output."""
    output_lines = []
    output_lines.append("Fetching and processing the most recent message...")
    print("Fetching and processing the most recent message...")
    raw = fetch_most_recgent_email()
    if raw is None:
        print("No messages found.")
        return
    main_text, attachments = extract_main_text_and_attachments(raw)
    print("Main text:")
    print(main_text)
    print("Attachments:", attachments)
    gemini_output = summarize_main_text_with_gemini(main_text)
    print("\nGemini output:")
    print(gemini_output)
    # Try to insert attachments into the Gemini output if it's JSON
    try:
        gemini_json = json.loads(gemini_output)
        if isinstance(gemini_json, dict):
            gemini_json["forwarder_attachments"] = attachments
            with open("output.txt", "w") as f:
                json.dump(gemini_json, f, indent=2)
            print("\nFinal output with attachments written to output.txt")
        else:
            with open("output.txt", "w") as f:
                f.write(gemini_output)
            print("\nGemini output written to output.txt (not JSON)")
    except Exception as e:
        with open("output.txt", "w") as f:
            f.write(gemini_output)
        print(f"\nGemini output written to output.txt (not JSON): {e}")