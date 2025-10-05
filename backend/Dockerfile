FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/entrypoint.sh

ENV FLASK_APP=app:create_app

CMD ["/app/entrypoint.sh"]
