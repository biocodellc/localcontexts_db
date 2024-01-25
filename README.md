# Local Contexts Hub Archived Repository

For the current repository, please visit the [Local Contexts Organization's repository](https://github.com/localcontexts/localcontextshub)
Prod Link:
- [Local Contexts Hub](https://localcontextshub.org/)

Branches:
- [Master](https://anth-ja77-local-contexts-8985.uc.r.appspot.com/)
- [Develop](https://anth-ja77-lc-dev-42d5.uc.r.appspot.com/)

Data sources:
- [Data used by Local Contexts Hub](https://github.com/biocodellc/localcontexts_json)
- [ROR API](https://api.ror.org)

## Getting Started
What you need to run this app:
- virtualenv
- Django 3.1
- PostGreSQL
- Python 3.8.3 with the latest version of `pip`


# Local Deployment

## First Time:  set up database
NOTE: See section below on Heroku vs. Local Deploymet and setting environment variables
```
psql> create database localcontextsdb # create the database
```

## Setup virtualenvironment
```
pyenv virtualenv 3.8.3 envi
```

Activate virtualenvironment:
```
source /Users/jdeck/.pyenv/versions/envi/bin/activate
```

## Install or Update Dependencies
Once in virtualenv, in the project root run:
```pip install -r requirements.txt```

## Initialize Environment Variables
Set localcontexts Environment Variables using EXPORT Statements
This will set local environment variables accessible via PYTHON

```source env-local.sh``` sets up environment variables for locally hosted database
```source env-localprod.sh``` sets up environment variables for production database to access it locally
```source env-localdev.sh``` sets up environment variables for development/testing database to access it locally

## Migration
```
python manage.py makemigrations
python manage.py migrate # sets up database
python manage.py createsuperuser # so you can start using database)
  Username: <Fill in your username>
  Email address: *<INSERT SITE_ADMIN_EMAIL> that is specified in the previous step, 'Initialize Environment Variables'*
```

## Production Maintenance Mode
A superuser can enable / disable maintenance mode by going to `/maintenance-mode/on` or `/maintenance-mode/off` which will show the `503.html` template to every user 
on the site letting users know site is under construction. Superuser will still have access to `/admin` and is the only user that can still make changes to the database at this time. 
*Maintenance mode should be turned on for production deplyment and turned off when deployment is complete.*

## Production Deployment and Migration
Every push to `master` will automatically trigger a new version build. Migrations should be done before pushing to `master`!!
In order to make migrations or migrate the production database:
1. `source env-localprod.sh`
2. CLOUD PROXY CONNECTION STRING
3. `python manage.py makemigrations`
4. `python manage.py migrate`
5. Merge `develop` into `master`

## Running the Server
```python manage.py runserver```

Locally, the app will start on port 8000.

Configuration can be found in the `settings.py` file.
Database models are located in `/<app name>/models.py`.

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

## Configuring GCP environment

The application is deployed into App Engine Standard serverless platform and uses managed
Postgres database via Cloud SQL deployment.

Prior to deploying the app one must go over the following steps in order to set up and 
configure the GCP project.

1. Configure the GCP project ID to be used by the `gcloud`: `gcloud config set <project-id>`.

2. Create App Engine app within the current GCP project and region.

   There may be only one app per GCP project and only inside one region so pick the app region 
   wisely. You will not be able to change it afterwards.
   
   You may use `gcloud app regions list` to list all the available App Engine regions.
   
   ```bash
   export REGION="us-central1"
   gcloud app create --region="${REGION}"
   ```
   
   One may also create a new App via the web console UI [here](https://console.cloud.google.com/appengine).

3. Create a new Cloud SQL Postgres instance.

   In order to create a new SQL instance it is recommended to use the web UI wizard 
   [here](https://console.cloud.google.com/sql/create-instance-postgres).
   
   The wizard default should cover some more-or-less generic workloads, but it may be a good
   idea to check out all the configuration options.
   
   After the instance creation navigate to the instance dashboard and copy the connection name.

4. Create Postgres DB.

   In order to create a new DB one may use the following command, or the Cloud SQL web UI.

   ```bash
   export DB_NAME="localcontextsdb"
   export INSTANCE="biocode-localcontests-db-stage:us-central1:biocode-db" # Change to real instance name
   gcloud sql databases create "${DB_NAME}" --instances="${INSTANCE}"
   ```
   
5. Migrate the DB.

   When the infrastructure is up it should be a good idea to roll out all the Django DB migrations
   as well as to create a Django superuser.
   
   To roll out the migrations do the following.

   * Start the Cloud SQL proxy: `cloud_sql_proxy --instances=<cloud-sql-connection-name>=tcp:5432`.
   * Make the migrations: `python manage.py makemigrations`.
   * Apply the migrations: `python manage.py migrate`

   To create a superuser run: `python manage.py createsuperuser`.

## Deploying the app

When the initial setup is done the app can be deployed with a single command: `gcloud app deploy`.

By default, the deployment promotes the newly deployed version and routes all the traffic to it.

In order to perform a deployment without routing the traffic add `--no-promote` option to the 
deployment command: `gcloud app deploy --no-promote`.

App Engine creates a new version for each deployment. The version name is the deployment date
and time. In order to supply a custom version name use `--version` option:
`gcloud app deploy --version="2021-02-06-v14"`.
