from dotenv import load_dotenv
from json import loads
import os


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
KEY_CONTENTS = loads(os.getenv("FIREBASE_JSON").replace("'", "\""))
