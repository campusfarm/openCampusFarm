"""Insta485 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# File Upload to var/uploads/
WEBAPI_ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/webAPI.sqlite3
DATABASE_FILENAME = WEBAPI_ROOT/'var'/'webAPI.sqlite3'
