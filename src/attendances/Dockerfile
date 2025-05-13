FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/attendances /app
RUN mkdir /app/db

CMD ["fastapi", "run", "--port", "8003"]
