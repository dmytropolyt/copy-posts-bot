import os
import pathlib

from dotenv import load_dotenv


load_dotenv(pathlib.Path(__file__).resolve().parent.parent / '.env')


TOKEN = os.environ.get('TOKEN')
API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
USERNAME = os.environ.get('USERNAME')
PHONE = os.environ.get('PHONE')

MEDIA_PATH = pathlib.Path(__file__).resolve().parent / 'media'
