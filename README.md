# Survey app

This project includes the survey web app.


## Setup

### Environment variables

* `BASE_URL` (required): Home page path where to redirect users;
* `APP_ID` (required): id of the application;
* `APP_SECRET` (required): secret code of the application;
* `WENET_INSTANCE` (required): the target wenet instance;
* django configuration:
    - `SECRET_KEY`: tha django secret key, the default set to `django-insecure-8jp0rb79f((j*#2604yhh5it&im25jni8@&t136ccnyb02yi_c`;
    - `DEBUG`: run django in debug mode, the default set to `True`;
    - `ALLOWED_HOSTS`: a list of allowed hosts divided by `;`, the default is set to `[]`.


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
