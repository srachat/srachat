# Base Image
FROM python:3

# set default environment variables
ENV PYTHONUNBUFFERED 1

# set working directory
RUN mkdir /srachat
WORKDIR /srachat

# This is a redundand step to optimize the build
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy project to working dir
COPY backend/ .

# Manual creating of static folder
RUN rm -rf srachat/static
RUN mkdir srachat/static

CMD sh -c " python3 manage.py collectstatic --noinput && \
            python3 manage.py migrate && \
            daphne root.asgi:application --port $PORT --bind 0.0.0.0 -v2"
