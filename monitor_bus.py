import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')
print(LINE_NOTIFY_TOKEN)