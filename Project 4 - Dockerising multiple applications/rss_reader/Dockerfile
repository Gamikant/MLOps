FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rss_reader.py .

RUN mkdir -p /app/images

CMD ["python", "rss_reader.py"]
