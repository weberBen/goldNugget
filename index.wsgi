#! /usr/bin/python3

import logging
import sys
import os

APP_PATH = "/home/user/www/"

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, APP_PATH)

from config import DEBUG, SECRET_KEY

from server import app as application


application.debug = DEBUG
application.secret_key = SECRET_KEY