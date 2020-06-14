from flask import Flask
import os
import logging


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, Friend!"


if __name__ == "__main__":
    PORT = int(os.environ.get("NIMBUS_ELASTIC_NLP_WORKER_PORT", 9010))

    DEBUG = os.environ.get("NIMBUS_ELASTIC_NLP_WORKER_PORT", False) is not False

    NIMBUS_ELASTIC_NLP_WORKER_PORT = os.environ.get("NIMBUS_ELASTIC_NLP_WORKER_PORT")
    ELASTIC_SEARCH_BASE_URL = os.environ.get("ELASTIC_SEARCH_BASE_URL")
    ELASTIC_SEARCH_INDEX_NAME = os.environ.get("ELASTIC_SEARCH_INDEX_NAME")
    NIMBUS_ELASTIC_NLP_WORKER_DEBUG = os.environ.get("NIMBUS_ELASTIC_NLP_WORKER_DEBUG")

    logging.info(f"NIMBUS_ELASTIC_NLP_WORKER_PORT: {NIMBUS_ELASTIC_NLP_WORKER_PORT}")
    logging.info(f"ELASTIC_SEARCH_BASE_URL: {ELASTIC_SEARCH_BASE_URL}")
    logging.info(f"ELASTIC_SEARCH_INDEX_NAME: {ELASTIC_SEARCH_INDEX_NAME}")
    logging.info(f"NIMBUS_ELASTIC_NLP_WORKER_DEBUG: {NIMBUS_ELASTIC_NLP_WORKER_DEBUG}")

    app.run(debug=True, host="0.0.0.0", port=PORT)
