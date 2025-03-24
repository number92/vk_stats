import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION", default="5.131")
ACCOUNT_ID: int = os.getenv("ACCOUNT_ID")
ID_CLIENT = os.getenv("ID_CLIENT")
ID_APP: int = os.getenv("ID_APP")
TODAY = datetime.today().strftime("%Y-%m-%d")
YESTERDAY = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
TIME = datetime.today().strftime("%H-%M-%S")
SERVICE_KEY = os.getenv("SERVICE_KEY")
URL = (
    "https://oauth.vk.com/authorize?client_id="
    + f"{os.getenv('ID_APP')}&display=page&redirect_uri="
    + "https://oauth.vk.com/blank.html&scope="
    + f"ads&response_type=token&v={VERSION}"
)

DATE_FROM = os.getenv("DATE_FROM")
DATE_TO = os.getenv("DATE_TO")


DF_COLUMNS = [
    "campaign_id",
    "compaign_name",
    "ad_id",
    "impressions",
    "clicks",
    "spent",
    "date",
    "reach",
    "link_external_clicks",
    "join_rate",
]
