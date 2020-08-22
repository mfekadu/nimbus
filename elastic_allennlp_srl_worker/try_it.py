from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from app_config import default_settings


es = AsyncElasticsearch(
    # could be multiple nodes
    hosts=[
        {
            "host": "elasticsearch-service",  # default_settings.get("ELASTIC_SEARCH_HOST"),
            "port": int(default_settings.get("ELASTIC_SEARCH_PORT")),
        }
    ],
    scheme=default_settings.get("ELASTIC_SEARCH_SCHEME"),
)


import asyncio


async def say(what, when):
    # https://asyncio.readthedocs.io/en/latest/hello_world.html
    await asyncio.sleep(when)
    print(what)


loop = asyncio.get_event_loop()
loop.run_until_complete(say("hello world", 1))


def _do(f):
    async def _f(*args, **kwargs):
        res = await f(*args, **kwargs)
        print(f"\t{f.__name__}(): {res}")

    return _f


print("pinging...")
loop.run_until_complete(_do(es.ping)())


print("trying refresh of `not_exist_index`...")
loop.run_until_complete(
    _do(es.indices.refresh)(
        index="not_exist_index", ignore_unavailable=True, allow_no_indices=True
    )
)


print("closing...")
loop.run_until_complete(_do(es.close)())
