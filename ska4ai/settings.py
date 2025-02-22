"""
Django settings for ska4ai project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import json
from pathlib import Path


home = Path.home()
with open(home / ".django_envs.json", "r") as f:
    django_envs = json.load(f)[0]


IS_PRODUCTION = django_envs["IS_PRODUCTION"]
# because windows doesn't support bool as env variables
if IS_PRODUCTION == "True":
    from .conf.production.settings import *
else:
    from .conf.development.settings import *