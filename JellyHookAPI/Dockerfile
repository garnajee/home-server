FROM python:alpine
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7777
CMD ["python", "jellyhookapi.py"]

