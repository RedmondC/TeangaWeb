FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8080

CMD ["gunicorn", "-b", ":8080", "main:app"]