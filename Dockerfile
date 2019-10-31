FROM python:3.7

COPY src /app
COPY data /app/data
COPY requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt
ARG DB_SECRET
RUN python main.py

CMD python main.py
