FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-u", "app/app.py"]
ENV FLASK_APP=app:create_app