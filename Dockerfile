# Base Image
FROM python:3

# set default environment variables
ENV PYTHONUNBUFFERED 1

# set working directory
RUN mkdir /srachat
WORKDIR /srachat
RUN mkdir backend
RUN mkdir frontend

# This is a redundand step to optimize the build
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy project to working dir
COPY backend/ backend/
# From the frontend we need just the built part
COPY frontend/build/ frontend/build/

WORKDIR backend

# Collecting static files
RUN python3 manage.py collectstatic --noinput

CMD sh -c "python3 manage.py migrate && daphne root.asgi:application --port $PORT --bind 0.0.0.0 -v2"
