import os
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client

HOME_DIR = Path(__file__).resolve().parent

load_dotenv(HOME_DIR / '.env')

# Secret key for secury session
SECRET_KEY = os.getenv('SECRET_KEY')

# Postgresql databse connection data
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

# Services for verify phone number
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
VERIFY_SERVICE_SID = os.getenv('VERIFY_SERVICE_SID')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
