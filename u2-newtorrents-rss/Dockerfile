FROM python:3.11-slim
ENV TZ=Asia/Shanghai PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY download_new_torrents.py /app/download_new_torrents.py
CMD ["python", "-u", "download_new_torrents.py"]
