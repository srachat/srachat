release: python backend/manage.py migrate
web: daphne srachat.asgi:application --port $PORT --bind 0.0.0.0 -v2
