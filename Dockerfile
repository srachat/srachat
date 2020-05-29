FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /srachat
WORKDIR /srachat
COPY backend/requirements.txt /srachat/
RUN pip install -r requirements.txt
COPY . /srachat/