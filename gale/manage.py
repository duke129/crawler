'''
Jan 2019

Author : Amit

The aim of this script is to Crawl a given website
And give back a API like result in the end
Result will be list - List of all the web pages
List will contain dicts - dicts will contain individual detail of every webpage
Dict Structure - Title(Title of the page), URL(URL of the page), Links(Links on that page)

'''

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Crawler.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
