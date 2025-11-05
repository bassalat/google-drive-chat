---
description: Set up Gmail downloader in current project with account selection
---

You are helping the user set up the Gmail downloader tool in their current project directory. Follow these steps:

1. **Check for existing setup**
   - Look for `.gmail-data/` directory
   - If it exists, inform the user and ask if they want to reconfigure

2. **List available accounts**
   - Run: `python ~/.gmail-accounts/account_manager.py list`
   - Show the user which accounts are available
   - If no accounts exist, guide them to add one first (see step 6)

3. **Ask user to select an account**
   - Use the AskUserQuestion tool to let them choose from available accounts
   - Include an "Add new account" option

4. **If adding a new account:**
   - Ask for account name (e.g., "work", "personal", "client-acme")
   - Ask for path to credentials.json file
   - Run: `python ~/.gmail-accounts/account_manager.py add <name> <path>`
   - Then proceed to setup with this new account

5. **Set up the project**
   - Copy gmail_client.py from the gmail-downloader repo to current directory
   - Run: `python ~/.gmail-accounts/account_manager.py setup <selected_account> .`
   - This will:
     - Create `.gmail-data/` directory
     - Copy credentials.json for the selected account
     - Copy token.json if it exists (already authenticated)
     - Create `.gmail-config` file
     - Update `.gitignore`

6. **Verify setup**
   - Check that `.gmail-data/credentials.json` exists
   - Check that `gmail_client.py` exists in current directory

7. **Inform the user**
   - Tell them setup is complete
   - Explain they need to authenticate if this is first time with this account
   - Show them how to test: `python -c "from gmail_client import GmailClient; c = GmailClient(); c.authenticate()"`
   - Tell them they can now use `/gmail-fetch` to download emails
   - Remind them that after first authentication, run: `python ~/.gmail-accounts/account_manager.py sync` to save the token for reuse

IMPORTANT:
- The gmail_client.py file location is: /Users/bassalat/Documents/tools/gmail-downloader/gmail_client.py
- Copy it to the current working directory (not .gmail-data/)
- The account_manager.py is at: ~/.gmail-accounts/account_manager.py
