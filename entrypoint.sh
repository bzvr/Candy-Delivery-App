#!/bin/sh
echo "Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"


python manage.py makemigrations candy_delivery_app
python manage.py migrate --noinput
python manage.py collectstatic --no-input --clear
python manage.py initadmin 

exec "$@"