import hishel
from hishel._utils import extract_header_values_decoded
from httpcore import Request, Response
from openai import AsyncOpenAI

from .log import log

httpx_client: hishel.AsyncCacheClient | None = None
oai_client: AsyncOpenAI | None = None


class IgnoreCacheController(hishel.Controller):
    def construct_response_from_cache(
        self, request: Request, response: Response, original_request: Request
    ) -> Response | Request | None:
        skip_cache_headers = extract_header_values_decoded(
            request.headers, b"skip-cache"
        )

        if skip_cache_headers == ["true"]:
            log.debug("Ignoring cache")
            return None

        log.debug("Using cache")

        return super().construct_response_from_cache(
            request, response, original_request
        )


def get_httpx_client():
    """
    Create or get a singleton httpx client with caching enabled.
    https://github.com/karpetrosyan/hishel
    """
    global httpx_client
    if httpx_client is None:
        storage = hishel.AsyncFileStorage()
        controller = IgnoreCacheController(
            # cacheable_methods=["GET", "POST"],
            cacheable_status_codes=[200],
            force_cache=True,
        )
        httpx_client = hishel.AsyncCacheClient(
            controller=controller,
            storage=storage,
        )
    return httpx_client


def get_oai_client():
    """
    Create or get a singleton async OpenAI client with requests caching enabled.
    """
    global oai_client
    if oai_client is None:
        httpx_client = get_httpx_client()
        oai_client = AsyncOpenAI(http_client=httpx_client)
    return oai_client


async def test_client_caching():
    client = get_httpx_client()

    # test get
    await client.get("https://httpbin.org/get", headers={"skip-cache": "true"})

    # test post
    await client.post("https://httpbin.org/post", json={"key": "value"})


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_client_caching())
