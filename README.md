# localcontexts_db
Branches:
- Master: Final location and config of LocalContexts (Live Site)
- Develop: dev branch for pushing changes
- heroku-demo: heroku config for live demo of [LocalContexts](https://localcontexts.herokuapp.com/)

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
NOTE: See section below on Heroku vs. Local Deploymet and setting environment variables
```
psql> create database localcontextsdb # create the database
python manage.py makemigrations
python manage.py migrate # sets up database
python manage.py createsuperuser # so you can start using database)
```

### Installing Dependencies
Once in virtualenv, in the project root run:
```pip install -r requirements.txt```

To run the app in dev:
```python manage.py runserver```

The app will start on port 8000, go to `8000/accounts/login` or `8000/accounts/register` to see the application.

** Note:
If creating a database for the first time, log into `/admin` as superuser and create a Group called `Site Administrator`, then go to `Users` and select user that has a valid email to add to this group.

Configuration can be found in the `settings.py` file.
Database models are located in `apps/accounts/models.py`.

### Heroku Deployment vs. Local Deployment
```source setupHeroku.sh``` sets up environment variables for heroku hosted database
```source setupLocal.sh``` sets up environment variables for locally hosted database

# GCP Deployment

## Prerequisites

1. Install [`gcloud`][gcloud] utility and login user appropriate account: `gcloud auth login --update-adc`.

2. Configure the default GCP project: `gcloud set project <projectId>`.

3. Download [Cloud SQL proxy][csql-proxy].

4. Start the proxy: `cloud_sql_proxy --instances=<cloud-sql-connection-name>=tcp:5432`.

   You can find the connection name at the Cloud SQL instance overview page.
   It has the following structure: `<gcp-project>:<region>:<instance-name>` e.g. 
   `biocode-localcontests-db:us-central1:biocode-db`.

Now you're able to start the local env but point to the Cloud DB. This may be useful 
if migrations should be applied.

[gcloud]: https://cloud.google.com/sdk/docs/install
[csql-proxy]: https://cloud.google.com/sql/docs/postgres/quickstart-proxy-test#install-proxy
