# SmartDesk AI Agent

A runnable portfolio prototype for a business-support assistant, built with Python and Streamlit. It retrieves relevant sections from a local Markdown knowledge base, offers optional web search, and can use an OpenAI model when configured. Without an API key, it runs in a basic retrieval-based demo mode.

## Requirements
- Python 3.10 or newer
- Windows / macOS / Linux
- Internet connection to install packages; OpenAI API key only for model-powered responses

## Run on Windows with VS Code
1. Extract the ZIP and open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run ` .venv\Scripts\activate.bat ` (without the leading space).
4. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Start the app:

   ```powershell
   streamlit run app.py
   ```
6. Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Optional OpenAI setup
Copy `.env.example` to `.env`, add your API key, and restart the app. The OpenAI API may incur charges. Never commit `.env` to GitHub.

## Optional web search
Turn on **Enable optional web search** in the sidebar. Web search requires a working connection and may fail due to provider limits. Treat results as unverified.

## Customize it
- Edit `knowledge_base.md` with fictional or authorized business details.
- Update branding and UI in `app.py`.
- Add a new tool or integration in `agent/core.py`.
- Test unsupported questions, API failures, and search failures.
- Take screenshots of your own running implementation for LinkedIn.

## Portfolio integrity
This is a starter project created for customization. Before presenting it publicly, make meaningful changes, test them, and describe your own contribution accurately. Do not claim paid client work or production use unless true.

## License
This starter is provided under the MIT License. Third-party packages have their own licenses.
