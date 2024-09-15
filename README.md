
## Requirements

Make sure you have [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) installed.

Also make sure to have OPENAI_API_KEY set in your environment variables.

## Installation

Install the project and its dependencies:

```bash
uv sync
```

Initialize the project:

```bash
uv run python -m lamp_chat.init
```

The last step does the following:
- Extract text from PDFs
- Parse each PDF (lamp) into a JSON description of the lamp via the OpenAI API
- Store the JSON descriptions in a SQLite database

## Usage

Run the following command to start the chatbot:

```bash
uv run python -m lamp_chat.ui
```

It starts a minimal UI where you can chat with the chatbot.