---
description: Fetch Gmail emails and make them available for analysis
---

You are helping the user fetch emails from Gmail for analysis. Follow these steps:

1. **Verify setup**
   - Check if `.gmail-data/` directory exists
   - Check if `gmail_client.py` exists in current directory
   - If not, inform user to run `/gmail-setup` first

2. **Parse the user's request**
   - Extract the query from their request (e.g., "from:boss@company.com", "subject:budget", etc.)
   - Determine how many emails to fetch (default to 10 if not specified)
   - Check if they want to download attachments (default: yes)

3. **Create a Python script to fetch emails**
   - Import gmail_client
   - Create GmailClient instance (no parameters needed - it auto-detects .gmail-data/)
   - Authenticate
   - Search for messages using the query
   - Download the messages with batch_download()

4. **Execute the fetch**
   - Run the Python script
   - Show progress to the user

5. **Present the results**
   - Read the downloaded JSON files from `.gmail-data/downloads/emails/`
   - Summarize what was found (count, subjects, senders, dates)
   - If user asked for analysis, perform it now
   - Show file locations for reference

6. **Handle errors gracefully**
   - If authentication fails, guide user to authenticate manually
   - If no emails found, inform clearly
   - If token expired, suggest re-authentication

Example queries:
- "from:john@example.com"
- "subject:meeting after:2024/10/01"
- "has:attachment is:unread"
- "in:inbox label:important"

IMPORTANT:
- Downloaded emails go to `.gmail-data/downloads/emails/msg_*.json`
- Attachments go to `.gmail-data/downloads/attachments/<message_id>/`
- Always show the user a summary of what was downloaded
- After downloading, analyze the content if that's what the user wants
