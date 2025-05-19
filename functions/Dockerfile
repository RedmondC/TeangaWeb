FROM python:3.13-slim

WORKDIR /python-docker
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8080

CMD ["gunicorn", "-b", ":8080", "main:app"]