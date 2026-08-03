FROM python:3.12-slim

WORKDIR /workspace

COPY database /workspace/database

COPY .env /workspace/.env

RUN pip install --no-cache-dir psycopg2-binary python-dotenv

CMD ["python","database/migrate.py"]
