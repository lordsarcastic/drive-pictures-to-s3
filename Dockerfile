# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install -U poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root --no-interaction --no-ansi

# Copy the content of the local src directory to the working directory
COPY ./drive_pictures_to_s3 ./drive_pictures_to_s3/

# Specify the command to run on container start
CMD ["python", "drive_pictures_to_s3/main.py"] 
