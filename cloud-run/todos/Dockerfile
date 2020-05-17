# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8.2-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install -y gcc libmariadb-dev

# Install production dependencies.
RUN python -m pip install --upgrade pip
RUN pip install sqlalchemy uvicorn fastapi mysqlclient

CMD exec uvicorn --reload --host "0.0.0.0" --port $PORT --workers 1 main:app
