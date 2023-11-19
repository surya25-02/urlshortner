python manage.py migrate --no-input 
python manage.py collectstatic

if [ -z "$PORT" ]; then
  export PORT=8000
fi

gunicorn -b 0.0.0.0:$PORT urlshortner.wsgi