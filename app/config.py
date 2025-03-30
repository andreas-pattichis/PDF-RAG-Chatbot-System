# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_CONNECTION_STR = os.getenv("MONGO_CONNECTION_STR")
