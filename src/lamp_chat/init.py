import asyncio
from collections import defaultdict
from pathlib import Path

import pymupdf  # imports the pymupdf library
from rich.progress import track

from lamp_chat.conf import conf
from lamp_chat.db import get_db
from lamp_chat.orm import Lamp

from .log import log
from .oai import get_oai_client

prompt = f"""\
Your task is to convert the text of a technical documentation of a lamp to a JSON representation using the following JSON schema:

```json
{Lamp.model_json_schema()}
```

You must only answer in JSON format.
The text will be in German and you should output German as well.
"""


async def create_lamp(pdf_text: str) -> Lamp:
    oai = get_oai_client()

    completion = await oai.beta.chat.completions.parse(
        model=conf.use_model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": pdf_text},
        ],
        response_format=Lamp,  # type: ignore
    )
    lamp = completion.choices[0].message.parsed

    assert lamp, "No lamp was created"

    return lamp


async def init_app():
    oai = get_oai_client()

    page = await oai.models.list()
    models = sorted([model.id for model in page.data])

    log.debug("Available models: ", models=models)

    db = await get_db(drop_tables=True)

    stem2text: dict[str, str] = defaultdict(str)

    # load pdfs from data dir
    for file in Path("pdfs").glob("*.pdf"):
        doc = pymupdf.open(file)
        for page in doc:  # iterate the document pages
            text = page.get_text()  # type: ignore
            stem2text[file.stem] += f"--- start page {page.number} ---\n"
            stem2text[file.stem] += text
            stem2text[file.stem] += f"--- end page {page.number} ---\n"

    assert stem2text, "No text was extracted from the PDFs"

    for stem, text in track(stem2text.items()):
        # print(Rule(stem))
        # print(text)
        log.info("Creating lamp...")
        lamp = await create_lamp(text)
        # print(lamp)
        async with db.get_session() as session:
            session.add(lamp)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(init_app())
