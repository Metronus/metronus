#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metronus.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    import django
    django.setup()

    argv = sys.argv[1]

    if argv == 'populate':
        #Load the data into the database
        from populate_database import populate_database
        populate_database()
    elif argv=='populaternd':
        #Load the data into the database
        from populate_database2 import randomLoad
        randomLoad()

    else:
        execute_from_command_line(sys.argv)
