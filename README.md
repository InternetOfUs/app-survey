# Survey app

This project includes the survey web app.


## Setup

### Environment variables

* BASE_PATH: Home page path where to redirect users;
* APP_ID: id of the application;
* APP_SECRET: secret code of the application;
* INSTANCE: the target wenet instance;
* general configuration
    - SECRET_KEY: tha django secret key;
    - DEBUG: run django in debug mode, default set to `True`;
    - ALLOWED_HOSTS: a list of hosts divided by `;` the default is set to [].


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

Create a superuser:

```bash
python manage.py createsuperuser
```
