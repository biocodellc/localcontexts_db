# localcontexts_db
Local contexts back-end

## Getting Started
What you need to run this app:
- virtualenv
- Django 3.1
- PostGreSQL
- Python 3.8.3 with the latest version of `pip`

### Installing Dependencies
Once in virtualenv, in the project root run:
```pip install -r requirements.txt```

To run the app:
```python manage.py runserver```

Configuration can be found in the `settings.py` file.
Database models are located in `apps/accounts/models.py`.