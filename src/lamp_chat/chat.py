import json
from typing import Any, Literal

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from sqlalchemy import text

from lamp_chat.conf import conf
from lamp_chat.db import get_db
from lamp_chat.oai import get_oai_client

from .orm import Lamp

console = Console()
table_repr = Lamp.model_json_schema()
# table_repr = CreateTable(Lamp.__table__)
system_prompt = f"""\
You are an employee of a German company that sells lamps.
Customers ask you various types of questions about your company's products.
To help you answer these questions, you have access to a sqlite database whose schema is as follows: 

```json
{table_repr}
```

For all string fields except for `id`, you should use the `LIKE` operator in your SQL queries to match case-insensitively and partially.
"""

console.print(system_prompt)


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
                        "description": "The SQL query to run on the lamp table.",
                    }
                },
                "required": ["sql"],
                "additionalProperties": False,
            },
        },
    }
]


class UIMessage(BaseModel):
    role: Literal["user", "bot"]
    content: str


class Chat:
    def __init__(self) -> None:
        self.oai_messages: list[Any] = []
        self.ui_messages: list[UIMessage] = []
        # Add the system prompt once during initialization
        self.oai_messages.append({"role": "system", "content": system_prompt})

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
        console.print(Align.right(panel) if role == "user" else Align.left(panel))

    async def lamp_query(self, sql: str, tool_call_id: str):
        assert isinstance(sql, str), "SQL query must be a string"
        self.print_message("system", f"Executing SQL query: {sql}")
        db = await get_db()
        cursor = await db.exec(text(sql))
        result = cursor.fetchall()

        self.print_message("system", f"Query result: {result}")

        tool_call_result_message: ChatCompletionMessageParam = {
            "role": "tool",
            "content": f"Query result: {result}",
            "tool_call_id": tool_call_id,
        }

        self.oai_messages.append(tool_call_result_message)

    async def chat(self, user_message: str = ""):
        oai = get_oai_client()

        # send user message
        self.oai_messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        self.print_message("user", user_message)

        response = await oai.chat.completions.create(
            model=conf.use_model,
            messages=self.oai_messages,
            tools=tools,
        )
        # add assistant response message to history
        assistant_message = response.choices[0].message
        self.oai_messages.append(assistant_message)  # type: ignore

        if assistant_message.content:
            self.print_message("assistant", assistant_message.content)

        # Check if tool was used
        sql: str | None = None
        tool_calls = response.choices[0].message.tool_calls

        if tool_calls:
            n_tool_calls = len(tool_calls)

            for i, tool_call in enumerate(tool_calls):
                args = json.loads(tool_call.function.arguments)
                assert isinstance(args, dict)
                self.print_message(
                    "assistant",
                    f"Tool call [{i+1}/{n_tool_calls}]: {tool_call.function.name}({args})",
                )
                if tool_call.function.name == "lamp_query":
                    sql = args["sql"]
                    assert isinstance(sql, str)
                    await self.lamp_query(sql, tool_call.id)

            response = await oai.chat.completions.create(
                model=conf.use_model, messages=self.oai_messages
            )

            # add assistant response to tool call result message to history
            assistant_message = response.choices[0].message
            self.oai_messages.append(assistant_message)
            if assistant_message.content:
                self.print_message("assistant", assistant_message.content)

    async def ui(self):
        try:
            while True:
                user_message = Prompt.ask("[bold cyan]You", console=console)
                await self.chat(user_message)
        except KeyboardInterrupt:
            console.print("[bold red]Goodbye![/bold red]")


if __name__ == "__main__":
    import asyncio

    chat = Chat()
    asyncio.run(chat.ui())
