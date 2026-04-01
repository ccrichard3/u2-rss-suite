FROM python:3.11-slim
ENV TZ=Asia/Shanghai PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY catch_magic.py /app/catch_magic.py
CMD ["python", "-u", "catch_magic.py"]
