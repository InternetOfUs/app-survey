# Survey app

This project includes the survey web app.


## Setup

### Required Python Packages

Required Python packages can be installed using the command:

```bash
pip install -r requirements.txt
```

### Environment variables

* `OAUTH_CALLBACK_URL` (required): the OAuth2 callback url (must be equal to the one set in the WeNet hub);
* `WENET_APP_ID` (required): id of the application;
* `WENET_APP_SECRET` (required): secret code of the application;
* `WENET_INSTANCE_URL:` (required): the url of the target WeNet instance;
* `SURVEY_FORM_ID:` (required): the identifier of the survey form;
* `BASE_URL`: Base url of the web app (e.g., `dev/`), the default set to `""`;
* `SECRET_KEY`: tha django secret key, the default set to `django-insecure-8jp0rb79f((j*#2604yhh5it&im25jni8@&t136ccnyb02yi_c`;
* `DEBUG`: run django in debug mode, the default set to `True`;
* `ALLOWED_HOSTS`: a list of allowed hosts divided by `;`, the default is set to `[]`.
* `CELERY_BROKER_URL` (required): the url of the celery broker.
* `DJANGO_DB`: the target database, default set to `sqlite3` the available value are:
  * `sqlite3`
  * `postgres`
* `PG_DATABASE`: the postgres database name, use only with the `postgres` option of the `DJANGO_DB` variable.
* `PG_USER`: the postgres user, use only with the `postgres` option of the `DJANGO_DB` variable.
* `PG_PASSWORD`: the postgres user's password, use only with the `postgres` option of the `DJANGO_DB` variable.
* `PG_HOST`: the postgres host, use only with the `postgres` option of the `DJANGO_DB` variable.
* `PG_PORT`: the port of the postgres server (default to 5432), use only with the `postgres` option of the `DJANGO_DB` variable.
* `SENTRY_DSN`: (Optional) The data source name for sentry, if not set the project will not create any event 
* `SENTRY_RELEASE`: (Optional) If set, sentry will associate the events to the given release
* `SENTRY_ENVIRONMENT`: (Optional) If set, sentry will associate the events to the given environment (ex. `production`, `staging`)


### Celery

Celery is configured to use the django db as result backend, so it is not necessary to configure a separate database for this.
However, it is necessary to configure a broker. The broker connection url must be specified in the `CELERY_BROKER_URL` environmental variable. 
In the project requirement file are already specified the dependencies for a sql broker. The simplest solution is tho create an empty
postgres database and set the `CELERY_BROKER_URL` in the following way:

```
sqla+postgresql://<postgres_username>:<postgress_password>@<postgres_host>:<postgres_port>/<database_name>
```

For a development environment is possible to use also a sqlite database, setting the `CELERY_BROKER_URL` in the following way:
```
sqla+sqlite:///db2.sqlite3
```


You can run the following command as many times you want in order to run several workers:

```bash
celery -A wenet_survey worker -B -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```


## Usage

Move in the _src_ directory:

```bash
cd src
```

Create the sqlite database and execute the migrations:

```bash
python manage.py migrate
```

Run the server:

```bash
python manage.py runserver
```

Create a superuser for accessing the admin page:

```bash
python manage.py createsuperuser
```

## Translations
In order to create the list of translation keys for a new language, use the following command (to be executed in the folder where the file `manage.py` lies):
```bash
django-admin makemessages -l <language code>
```
where the language code should correspond to one of the languages specified in the `settings.py` file, in the `LANGUAGES` variable

In order to refresh the list of translation keys, use the following command (to be executed in the folder where the file `manage.py` lies):
```bash
django-admin makemessages -a
```

To compile the translations, use the following:
```bash
django-admin compilemessages
```