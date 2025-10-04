FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-m", "flask", "--debug", "run", "--host=0.0.0.0", "--port=8000"]
ENV FLASK_APP=app:create_app