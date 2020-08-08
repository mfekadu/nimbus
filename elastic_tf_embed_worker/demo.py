#!/usr/bin/env python3
"""
This file is useful to quickly trying out some elasticsearch code.
"""

from elasticsearch import Elasticsearch
from app_config import default_settings


if __name__ == "__main__":
    es = Elasticsearch(
        hosts=[
            {
                "host": "elasticsearch-service",  # default_settings["ELASTIC_SEARCH_HOST"]
                "port": default_settings["ELASTIC_SEARCH_PORT"],
            }
        ],
        scheme=default_settings["ELASTIC_SEARCH_SCHEME"],
    )

    es.ping()

    index_name = default_settings["ELASTIC_SEARCH_DEFAULT_INDEX"]
    request_body = ""

    es.search(index=index_name, body=request_body)