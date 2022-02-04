from flask import Flask

app = Flask(__name__)

from src.config import *
from src.helpers import *
from src.jwt import *
from src.database import *
from src.views import *
