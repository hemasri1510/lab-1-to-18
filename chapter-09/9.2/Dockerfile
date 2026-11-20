FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pymongo
COPY . /app
CMD ["python", "lab9_2_partition_observer.py"]
