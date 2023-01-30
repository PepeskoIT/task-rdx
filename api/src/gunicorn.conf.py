import logging

from envs import WSGI_LOG_LEVEL, WSGI_PORT, WSGI_WORKERS_COUNT
from logging_setup import load_logger_config

load_logger_config()
logger = logging.getLogger("gunicorn.glogging.Logger")

bind = f"0.0.0.0:{WSGI_PORT}"
workers = WSGI_WORKERS_COUNT
loglevel = WSGI_LOG_LEVEL
worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "main:app"


def when_ready(server):
    logger.info('WSGI starting up')


def on_exit(server):
    logger.info('WSGI shutting down')
