# Clubber
Es handelt sich um ein primitives Buchungssystem welches aktuell zur Veranstaltungsorganisation des MeerManege e. V. Zirkusvereins eingesetzt wird. Aktuell ist das Userinterface nur in deutscher Sprache verfügbar.

## Installation 
Create python environment, e.g. in /var/clubber
```
python3 -m venv venv
```

Go into env and install python modules
```
source venv/bin/activate
pip install -r requirements.txt
```

Configure clubber in `config/settings.yml` and place your custom `logo.png` and `favicon.png` pictures in the `config` folder.

For postgres create database
```
CREATE DATABASE clubber;
CREATE USER clubber WITH PASSWORD 'clubber';
ALTER ROLE clubber SET client_encoding TO 'utf8';
ALTER ROLE clubber SET default_transaction_isolation TO 'read committed';
ALTER ROLE clubber SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE clubber TO clubber;
```

Create/Update database tabes
```
python manage.py makemigrations events
python manage.py migrate
```

Run development server for testing only
```
python manage.py runserver
```

For production run
```
python manage.py collectstatic
```
to copy all static files to `static_ext`.

## How to start
1. Create admin user by running `python manage.py createsuperuser`.
2. Login to webinterface using this new account and set a valid e-mail and update notification setting (Einstellungen -> E-Mail)
3. Add at least one event type (Einstellungen -> Veranstaltungsarten)
4. Create your first event (Neues Treffen)
