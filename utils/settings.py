import logging

from logging.config import dictConfig
from json import load
from dotenv import load_dotenv
from os import getenv, listdir

load_dotenv()
TOKEN = getenv("TOKEN")
LOGGING_CHANNEL = int(getenv("LOGGING_CHANNEL"))
WELCOME_CHANNEL_ID = int(getenv("WELCOME_CHANNEL"))

COGS_DIR = listdir('cogs')
VOICE_COGS_DIR = listdir('voice_cogs')

COGS = COGS_DIR + VOICE_COGS_DIR

file = open('utils/loggers.json')
logger_data = load(file)

dictConfig(logger_data)
