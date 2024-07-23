import os

from jinja2 import Environment, FileSystemLoader
from markdownify import markdownify

from textcube_to_jekyll import filters

BASE_DIR = os.path.dirname(__file__)

file_loader = FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
env = Environment(loader=file_loader)

env.filters['markdownify'] = markdownify
env.filters['json'] = filters.encode_json
env.filters['date_format'] = filters.date_format
env.filters['convert_ttml'] = filters.convert_ttml


def get_template(filename: str):
    return env.get_template(filename)

