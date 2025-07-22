import json

from gemini_email_preformatter import extract_main_text_and_attachments, summarize_main_text_with_gemini
from gmail_fetch.gmail_api_mail_fetch import fetch_most_recent_email

def version_2():
    """Fetches the most recent message in the user's inbox, extracts main text and attachments, sends to Gemini, and prints/writes the structured output."""
    output_lines = []
    output_lines.append("Fetching and processing the most recent message...")
    print("Fetching and processing the most recent message...")
    raw = fetch_most_recent_email()
    if raw is None:
        print("No messages found.")
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write("No messages found.\n")
        return
    # Extract main text and attachments
    main_text, attachments = extract_main_text_and_attachments(raw)
    output_lines.append("Main text:")
    output_lines.append(main_text)
    print("Main text:")
    print(main_text)
    output_lines.append("Attachments:")
    output_lines.append(str(attachments))
    print("Attachments:")
    print(attachments)
    # Call Gemini to get structured output
    gemini_output = summarize_main_text_with_gemini(main_text)
    print("Gemini output:")
    print(gemini_output)
    output_lines.append("Gemini output:")
    output_lines.append(gemini_output)
    # Try to insert attachments into the correct field in the JSON output
    try:
        gemini_json = json.loads(gemini_output)
        # Insert attachments into the top-level field if present
        if isinstance(gemini_json, dict):
            gemini_json["forwarder_attachments"] = attachments
            final_output = json.dumps(gemini_json, indent=2, ensure_ascii=False)
            print("\nFinal output with attachments:")
            print(final_output)
            output_lines.append("Final output with attachments:")
            output_lines.append(final_output)
        else:
            # If not a dict, just output as is
            output_lines.append("(Gemini output not JSON)")
    except Exception as e:
        output_lines.append(f"(Could not parse Gemini output as JSON: {e})")
    # Write all output to a txt file
    with open("output.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(f"{line}\n")