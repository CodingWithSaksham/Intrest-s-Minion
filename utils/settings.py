import logging

from logging.config import dictConfig
from json import load
from dotenv import load_dotenv
from os import getenv, listdir

load_dotenv()
TOKEN = getenv("TOKEN")
LOGGING_CHANNEL = int(getenv("LOGGING_CHANNEL"))
WELCOME_CHANNEL_ID = int(getenv("WELCOME_CHANNEL"))
BOT_CMD_ID = int(getenv("BOT_CMD_CHANNEL"))

COGS_DIR = listdir('cogs')

file = open('utils/loggers.json')
logger_data = load(file)

dictConfig(logger_data)
