import json
from typing import Any, Literal

from openai.types.chat import ChatCompletionMessageParam
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from sqlalchemy import text

from lamp_chat.conf import conf
from lamp_chat.db import get_db
from lamp_chat.oai import get_oai_client

from .log import log
from .orm import Lamp

table_repr = Lamp.model_json_schema()


system_prompt = f"""\
You are an employee of a German company that sells lamps.
Customers ask you various types of questions about your company's products.
To help you answer these questions, you have access to a sqlite database whose schema is as follows: 

```json
{table_repr}
```

For all string fields except for `id`, you should use the `LIKE` operator in your SQL queries to match case-insensitively and partially.
"""


tools = [
    {
        "type": "function",
        "function": {
            "name": "lamp_query",
            "description": "Run a SQL query on the lamp table.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to run on the lamp table. Must not contain any curly braces.",
                    }
                },
                "required": ["sql"],
                "additionalProperties": False,
            },
        },
    }
]


class Chat:
    def __init__(self, console: Console | None = None) -> None:
        self.oai_messages: list[Any] = []

        self.oai_messages.append({"role": "system", "content": system_prompt})

        self.console = console or Console()

    def print_message(self, role: Literal["user", "system", "assistant"], content: str):
        if role == "user":
            title = "[bold cyan]You[/bold cyan]"
            border_style = "cyan"
        elif role == "system":
            title = "[bold green]System[/bold green]"
            border_style = "green"
        elif role == "assistant":
            title = "[bold magenta]Assistant[/bold magenta]"
            border_style = "magenta"
        else:
            raise ValueError(f"Invalid role: {role}")
        panel = Panel(
            Text(content, style="bold white"),
            title=title,
            border_style=border_style,
            padding=(1, 2),
            width=60,
        )
        self.console.print(Align.right(panel) if role == "user" else Align.left(panel))

    async def lamp_query(self, sql: str, tool_call_id: str):
        """
        - Run a SQL query on the lamp table
        - Add tool message with the query result to history
        """
        log.info(f"Executing SQL query: {sql}")
        db = await get_db()
        cursor = await db.exec(text(sql))
        result = cursor.fetchall()

        log.info(f"Query result: {result}")

        tool_call_result_message: ChatCompletionMessageParam = {
            "role": "tool",
            "content": f"Query result: {result}",
            "tool_call_id": tool_call_id,
        }

        self.oai_messages.append(tool_call_result_message)

    async def send_user_message(self, user_message: str):
        """
        - Send user message to OpenAI API
        - Receive assistant response
        - Print assistant response
        """

        oai = get_oai_client()

        # send user message
        self.oai_messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = await oai.chat.completions.create(
            model=conf.use_model,
            messages=self.oai_messages,
            tools=tools,  # type: ignore
        )
        # add assistant message to history
        assistant_message = response.choices[0].message
        self.oai_messages.append(assistant_message)  # type: ignore

        if assistant_message.content:
            self.print_message("assistant", assistant_message.content)

        # Check if tool was used
        sql: str | None = None
        tool_calls = response.choices[0].message.tool_calls

        if tool_calls:
            n_tool_calls = len(tool_calls)

            # iterate over tool calls
            for i, tool_call in enumerate(tool_calls):
                args = json.loads(tool_call.function.arguments)
                assert isinstance(args, dict)
                log.info(
                    f"Tool call [{i+1}/{n_tool_calls}]: {tool_call.function.name}({args})",
                )
                if tool_call.function.name == "lamp_query":
                    sql = args["sql"]
                    assert isinstance(sql, str)
                    await self.lamp_query(sql, tool_call.id)

            response = await oai.chat.completions.create(
                model=conf.use_model, messages=self.oai_messages
            )

            # add assistant's reaction to tool result to history
            assistant_message = response.choices[0].message
            self.oai_messages.append(assistant_message)
            if assistant_message.content:
                self.print_message("assistant", assistant_message.content)

    async def ui(self):
        try:
            while True:
                user_message = self.console.input("[bold cyan]You: ")
                await self.send_user_message(user_message)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log.error(str(e))


if __name__ == "__main__":
    import asyncio

    try:
        chat = Chat()
        asyncio.run(chat.ui())
    except KeyboardInterrupt:
        pass
