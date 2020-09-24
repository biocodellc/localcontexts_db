# localcontexts_db
Local contexts back-end

## Getting Started
What you need to run this app:
- virtualenv
- Django 3.1
- PostGreSQL
- Python 3.8.3 with the latest version of `pip`

### Installing Dependencies
Setup virtualenvironment:
```
pyenv virtualenv 3.8.3 envi
```

Activate virtualenvironment:
```
source /Users/jdeck/.pyenv/versions/envi/bin/activate
```

### Setting up
Set localcontexts Environment Variables using EXPORT Statements
This will set local environment variables accessible via PYTHON
# TODO use a file to set these instead of Environment Variables


Set up database:
```
psql> create database localcontextsdb # create the database
python manage.py makemigrations
python manage.py migrate # sets up database
python manage.py createsuperuser # so you can start using database)
```

### Installing Dependencies
Once in virtualenv, in the project root run:
```pip install -r requirements.txt```

To run the app:
```python manage.py runserver```

Configuration can be found in the `settings.py` file.
Database models are located in `apps/accounts/models.py`.
