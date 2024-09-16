# Lamp Chat

## Requirements

Make sure you have [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) installed.

Also make sure to have OPENAI_API_KEY set in your environment variables.

## Usage

Initialize the project:

```bash
uv run python -m lamp_chat.init
```

The last step takes a couple minutes, and does the following:
- Extract text from PDFs inside the `./pdfs` directory
- Use [OpenAI's Structured Generation](https://platform.openai.com/docs/guides/structured-outputs/introduction) to parse each PDF text (unstructured lamp description) into a JSON object defined by a SQLModel schema (`./src/lamp_chat/orm.py`).
- Store the parsed JSON objects in a SQLite database.

Then, run the following command to start a minimal chat UI:

```bash
uv run python -m lamp_chat.chat
```

The bot uses [OpenAI's Function Calling](https://platform.openai.com/docs/guides/function-calling) feature to generate SQL queries against the database of lamp descriptions.
Through this, the bot can answer detailed questions about the lamps that are grounded in the data, and prevents it from hallucinating.