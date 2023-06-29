FROM python:3.11-slim

RUN apt update && \
    apt upgrade -y && \
    apt install -y ffmpeg libsndfile1 libsndfile1-dev

COPY app /app

WORKDIR /app

RUN cd /app && \
    pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "app:app"]
